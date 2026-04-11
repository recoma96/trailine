import argparse
import json
import math
from dataclasses import dataclass, field
from typing import Any

from geoalchemy2 import WKTElement
from geoalchemy2.functions import ST_DWithin, ST_Distance
from sqlalchemy.orm import Session

from trailine_model.models.course import CourseInterval, CourseIntervalDifficulty
from trailine_model.models.place import Place
from trailine_scripts.common.database import get_db


class GeoJSONValidationError(ValueError):
    """GeoJSON 포맷이 유효하지 않을 때 발생하는 예외."""
    pass


@dataclass
class CoursePoint:
    longitude: float
    latitude: float
    elevation: float


@dataclass
class SegmentWaypoint:
    name: str
    location: CoursePoint
    description: str | None = None


@dataclass
class SegmentMetadata:
    title: str
    duration_forward_min: int
    duration_backward_min: int
    start: SegmentWaypoint
    end: SegmentWaypoint
    description_forward: str | None = None
    description_backward: str | None = None


@dataclass
class CourseSegment:
    order: int
    metadata: SegmentMetadata
    coordinates: list[CoursePoint]
    segment_id: str | None = None
    color: str | None = None


@dataclass
class Course:
    name: str
    segments: list[CourseSegment] = field(default_factory=list)


class GeoJSONParser:
    """GeoJSON Dict를 Course 객체로 역직렬화하는 파서.

    포맷이 유효하지 않으면 GeoJSONValidationError를 발생시킨다.
    """

    def parse(self, data: Any) -> Course:
        self._require(isinstance(data, dict), "최상위 데이터는 객체여야 합니다.")
        self._require(
            data.get("type") == "FeatureCollection",
            "type 필드는 'FeatureCollection'이어야 합니다.",
        )

        features = data.get("features")
        self._require(
            isinstance(features, list) and len(features) > 0,
            "features는 하나 이상의 요소를 가진 배열이어야 합니다.",
        )

        segments: list[CourseSegment] = []
        course_name: str | None = None
        for idx, raw_feature in enumerate(features):
            segment, feature_course_name = self._parse_segment(raw_feature, idx)
            # 맨 첫번째 feature의 courseName을 코스 이름으로 사용한다.
            # 이후 feature의 courseName은 무시한다.
            if course_name is None:
                course_name = feature_course_name
            segments.append(segment)

        assert course_name is not None  # features가 비어있지 않음이 위에서 검증됨
        segments.sort(key=lambda s: s.order)
        return Course(name=course_name, segments=segments)

    def _parse_segment(self, raw: Any, idx: int) -> tuple[CourseSegment, str]:
        self._require(isinstance(raw, dict), f"features[{idx}]는 객체여야 합니다.")
        self._require(
            raw.get("type") == "Feature",
            f"features[{idx}].type은 'Feature'여야 합니다.",
        )

        geometry = raw.get("geometry")
        self._require(
            isinstance(geometry, dict), f"features[{idx}].geometry는 객체여야 합니다."
        )
        self._require(
            geometry.get("type") == "LineString",
            f"features[{idx}].geometry.type은 'LineString'이어야 합니다.",
        )

        raw_coords = geometry.get("coordinates")
        self._require(
            isinstance(raw_coords, list) and len(raw_coords) >= 2,
            f"features[{idx}].geometry.coordinates는 시작/끝점을 위해 "
            f"2개 이상의 좌표를 가져야 합니다.",
        )
        coordinates = [
            self._parse_coordinate(p, idx, i) for i, p in enumerate(raw_coords)
        ]

        properties = raw.get("properties")
        self._require(
            isinstance(properties, dict),
            f"features[{idx}].properties는 객체여야 합니다.",
        )

        order = properties.get("order")
        self._require(
            self._is_int(order),
            f"features[{idx}].properties.order는 정수여야 합니다.",
        )

        course_name = properties.get("courseName")
        self._require(
            isinstance(course_name, str) and course_name.strip() != "",
            f"features[{idx}].properties.courseName은 비어있지 않은 문자열이어야 합니다.",
        )

        segment_id = self._optional_str(
            properties.get("segmentId"), f"features[{idx}].properties.segmentId"
        )
        color = self._optional_str(
            properties.get("color"), f"features[{idx}].properties.color"
        )

        metadata = self._parse_metadata(properties.get("metadata"), coordinates, idx)

        segment = CourseSegment(
            order=order,
            metadata=metadata,
            coordinates=coordinates,
            segment_id=segment_id,
            color=color,
        )
        return segment, course_name

    def _parse_metadata(
        self,
        raw: Any,
        coordinates: list[CoursePoint],
        feature_idx: int,
    ) -> SegmentMetadata:
        base = f"features[{feature_idx}].properties.metadata"
        self._require(isinstance(raw, dict), f"{base}은(는) 객체여야 합니다.")

        title = raw.get("title")
        self._require(
            isinstance(title, str) and title.strip() != "",
            f"{base}.title은 비어있지 않은 문자열이어야 합니다.",
        )

        duration_forward_min = raw.get("durationForwardMin")
        self._require(
            self._is_int(duration_forward_min),
            f"{base}.durationForwardMin은 정수여야 합니다.",
        )

        duration_backward_min = raw.get("durationBackwardMin")
        self._require(
            self._is_int(duration_backward_min),
            f"{base}.durationBackwardMin은 정수여야 합니다.",
        )

        description_forward = self._optional_str(
            raw.get("descriptionForward"), f"{base}.descriptionForward"
        )
        description_backward = self._optional_str(
            raw.get("descriptionBackward"), f"{base}.descriptionBackward"
        )

        start = self._parse_waypoint(
            raw.get("start"), coordinates[0], f"{base}.start"
        )
        end = self._parse_waypoint(
            raw.get("end"), coordinates[-1], f"{base}.end"
        )

        return SegmentMetadata(
            title=title,
            duration_forward_min=duration_forward_min,
            duration_backward_min=duration_backward_min,
            start=start,
            end=end,
            description_forward=description_forward,
            description_backward=description_backward,
        )

    def _parse_waypoint(
        self,
        raw: Any,
        location: CoursePoint,
        path: str,
    ) -> SegmentWaypoint:
        self._require(isinstance(raw, dict), f"{path}은(는) 객체여야 합니다.")

        name = raw.get("name")
        self._require(
            isinstance(name, str) and name.strip() != "",
            f"{path}.name은 비어있지 않은 문자열이어야 합니다.",
        )

        description = self._optional_str(
            raw.get("description"), f"{path}.description"
        )
        # 빈 문자열은 설명이 없는 것으로 간주한다.
        if description == "":
            description = None

        return SegmentWaypoint(name=name, location=location, description=description)

    def _parse_coordinate(
        self, raw: Any, feature_idx: int, point_idx: int
    ) -> CoursePoint:
        self._require(
            isinstance(raw, (list, tuple)) and len(raw) == 3,
            f"features[{feature_idx}].geometry.coordinates[{point_idx}]는 "
            f"[longitude, latitude, elevation] 3개 원소의 배열이어야 합니다.",
        )
        lon, lat, ele = raw
        self._require(
            all(
                isinstance(v, (int, float)) and not isinstance(v, bool)
                for v in (lon, lat, ele)
            ),
            f"features[{feature_idx}].geometry.coordinates[{point_idx}]의 값은 "
            f"모두 숫자여야 합니다.",
        )
        return CoursePoint(
            longitude=float(lon), latitude=float(lat), elevation=float(ele)
        )

    @staticmethod
    def _require(condition: bool, message: str) -> None:
        if not condition:
            raise GeoJSONValidationError(message)

    @staticmethod
    def _is_int(value: Any) -> bool:
        # bool은 int의 subclass이지만 의미상 제외한다.
        return isinstance(value, int) and not isinstance(value, bool)

    @classmethod
    def _optional_str(cls, value: Any, path: str) -> str | None:
        if value is None:
            return None
        cls._require(isinstance(value, str), f"{path}은(는) 문자열이어야 합니다.")
        return value


class PlaceUpserter:
    """Course의 waypoint들을 Place로 DB에 업서트하는 헬퍼.

    각 waypoint에 대해 반경 SEARCH_RADIUS_M 이내의 기존 Place가 있다면
    가장 가까운 Place 하나를 재사용하고, 없다면 새 Place를 생성한다.
    """

    SEARCH_RADIUS_M = 50

    def __init__(self, db: Session):
        self.db = db

    def upsert(self, course: Course) -> list[Place]:
        """반환 리스트는 waypoint 순서와 동일하며, 길이는 segments + 1이다."""
        waypoints = self._collect_waypoints(course)

        places: list[Place] = []
        for waypoint in waypoints:
            places.append(self._upsert_one(waypoint))
        return places

    def _upsert_one(self, waypoint: SegmentWaypoint) -> Place:
        point = self._waypoint_to_wkt(waypoint)

        # 50m 이내에서 가장 가까운 기존 Place 조회 (Place.geom은 Geography라 미터 단위)
        nearest = (
            self.db.query(Place)
            .filter(ST_DWithin(Place.geom, point, self.SEARCH_RADIUS_M))
            .order_by(ST_Distance(Place.geom, point))
            .first()
        )
        if nearest is not None:
            return nearest

        new_place = Place(
            name=waypoint.name,
            geom=point,
            geog=point,
            elevation=int(round(waypoint.location.elevation)),
            description=waypoint.description,
        )
        self.db.add(new_place)
        # 다음 waypoint 검색 시 방금 추가된 Place도 후보가 되도록 flush
        self.db.flush()
        return new_place

    @staticmethod
    def _collect_waypoints(course: Course) -> list[SegmentWaypoint]:
        """Course의 segments로부터 Place로 업로드할 waypoints를 순서대로 추출한다.

        인접한 segment 간 end/start는 동일한 지점이므로, 각 segment의 start만 취하고
        마지막 segment의 end를 한 번 더 추가한다. 결과 길이는 segments + 1이다.
        """
        waypoints: list[SegmentWaypoint] = [
            segment.metadata.start for segment in course.segments
        ]
        # 마지막 segment의 end는 이후에 매칭되는 start가 없으므로 직접 추가
        waypoints.append(course.segments[-1].metadata.end)
        return waypoints

    @staticmethod
    def _waypoint_to_wkt(waypoint: SegmentWaypoint) -> WKTElement:
        loc = waypoint.location
        return WKTElement(f"POINT({loc.longitude} {loc.latitude})", srid=4326)


class CourseIntervalUpserter:
    """Course의 각 segment를 CourseInterval로 DB에 업서트하는 헬퍼.

    CourseInterval은 무향 간선으로 취급되며 `place_a_id < place_b_id` 제약을 가진다.
    따라서 필요 시 a/b를 스왑하고 그에 맞춰 정/역방향 데이터(description, duration,
    geom의 좌표 순서)도 함께 뒤집는다.

    중복 판정:
    - 동일한 Place 쌍(방향 무관)을 잇는 CourseInterval 중 `name`까지 일치하면
      기존 인스턴스를 재사용한다.
    """

    def __init__(self, db: Session):
        self.db = db
        self._default_difficulty_id: int | None = self._find_default_difficulty_id()

    def upsert(self, course: Course, places: list[Place]) -> list[CourseInterval]:
        """places는 PlaceUpserter.upsert() 결과 (길이 = segments + 1).

        반환 리스트는 course.segments 순서와 동일하다.
        """
        assert len(places) == len(course.segments) + 1, (
            "places 길이는 segments + 1 이어야 합니다."
        )

        intervals: list[CourseInterval] = []
        for i, segment in enumerate(course.segments):
            start_place = places[i]
            end_place = places[i + 1]
            intervals.append(self._upsert_one(segment, start_place, end_place))
        return intervals

    def _upsert_one(
        self,
        segment: CourseSegment,
        start_place: Place,
        end_place: Place,
    ) -> CourseInterval:
        meta = segment.metadata

        # place_a_id < place_b_id 제약을 만족하도록 정렬하고,
        # ab/ba 방향 데이터도 그에 맞춰 뒤집는다.
        if start_place.id < end_place.id:
            place_a, place_b = start_place, end_place
            description_ab = meta.description_forward
            description_ba = meta.description_backward
            duration_ab = meta.duration_forward_min
            duration_ba = meta.duration_backward_min
            ordered_coords = segment.coordinates
        else:
            place_a, place_b = end_place, start_place
            description_ab = meta.description_backward
            description_ba = meta.description_forward
            duration_ab = meta.duration_backward_min
            duration_ba = meta.duration_forward_min
            ordered_coords = list(reversed(segment.coordinates))

        # 동일 Place 쌍 + 동일 name인 CourseInterval이 있다면 재사용
        existing = (
            self.db.query(CourseInterval)
            .filter(
                CourseInterval.place_a_id == place_a.id,
                CourseInterval.place_b_id == place_b.id,
                CourseInterval.name == meta.title,
            )
            .first()
        )
        if existing is not None:
            return existing

        length_m = self._compute_length_m(segment.coordinates)
        geom_wkt = WKTElement(
            self._coords_to_linestring_z_wkt(ordered_coords),
            srid=4326,
            extended=True,
        )

        new_interval = CourseInterval(
            name=meta.title,
            description_ab=description_ab,
            description_ba=description_ba,
            geom=geom_wkt,
            place_a_id=place_a.id,
            place_b_id=place_b.id,
            course_interval_difficulty_id=self._default_difficulty_id,
            length_m=length_m,
            duration_ab_minutes=duration_ab,
            duration_ba_minutes=duration_ba,
        )
        self.db.add(new_interval)
        self.db.flush()
        return new_interval

    def _find_default_difficulty_id(self) -> int | None:
        """CourseIntervalDifficulty.level == 0 인 기본 난이도 ID를 조회한다."""
        difficulty = (
            self.db.query(CourseIntervalDifficulty)
            .filter(CourseIntervalDifficulty.level == 0)
            .first()
        )
        return difficulty.id if difficulty is not None else None

    @staticmethod
    def _coords_to_linestring_z_wkt(coordinates: list[CoursePoint]) -> str:
        parts = [f"{c.longitude} {c.latitude} {c.elevation}" for c in coordinates]
        return f"LINESTRINGZ({', '.join(parts)})"

    @staticmethod
    def _compute_length_m(coordinates: list[CoursePoint]) -> int:
        """인접 좌표 간 Haversine 거리 총합을 m 단위 정수로 반환한다.

        해발고도는 계산에서 제외한다.
        """
        earth_radius_m = 6_371_000.0
        total = 0.0
        for prev, curr in zip(coordinates, coordinates[1:]):
            phi1 = math.radians(prev.latitude)
            phi2 = math.radians(curr.latitude)
            dphi = math.radians(curr.latitude - prev.latitude)
            dlambda = math.radians(curr.longitude - prev.longitude)
            a = (
                math.sin(dphi / 2) ** 2
                + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            total += earth_radius_m * c
        return int(round(total))


def print_course_summary(course: Course) -> None:
    """역직렬화된 Course 객체의 내용을 사람이 읽기 좋은 형태로 출력한다."""
    print("=" * 60)
    print(f"코스명       : {course.name}")
    print(f"구간 수      : {len(course.segments)}")
    print("=" * 60)

    for segment in course.segments:
        meta = segment.metadata
        print(f"\n[구간 {segment.order}] {meta.title}")
        if segment.segment_id is not None:
            print(f"  segmentId          : {segment.segment_id}")
        if segment.color is not None:
            print(f"  color              : {segment.color}")
        print(f"  좌표 개수          : {len(segment.coordinates)}")
        print(
            f"  소요시간(정방향)   : {meta.duration_forward_min}분"
            f"  /  (역방향): {meta.duration_backward_min}분"
        )
        if meta.description_forward is not None:
            print(f"  정방향 설명        : {meta.description_forward}")
        if meta.description_backward is not None:
            print(f"  역방향 설명        : {meta.description_backward}")

        start = meta.start
        print(
            f"  시작점             : {start.name} "
            f"(lon={start.location.longitude}, lat={start.location.latitude}, "
            f"ele={start.location.elevation})"
        )
        if start.description is not None:
            print(f"    └ 설명           : {start.description}")

        end = meta.end
        print(
            f"  끝점               : {end.name} "
            f"(lon={end.location.longitude}, lat={end.location.latitude}, "
            f"ele={end.location.elevation})"
        )
        if end.description is not None:
            print(f"    └ 설명           : {end.description}")


def main():
    parser = argparse.ArgumentParser(description="GeoJSON 기반의 코스 데이터를 DB에 업로드")
    parser.add_argument("--file", required=True, help="Path to the GeoJSON file")

    args = parser.parse_args()

    # GeoJSON 파일 불러오기
    print(f"Reading {args.file}...")
    with open(args.file, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    try:
        # GeoJSON 데이터를 객체로 역직렬화
        course = GeoJSONParser().parse(geojson)
    except GeoJSONValidationError as e:
        print(f"Invalid GeoJSON format: {e}")
        return

    # 역직렬화된 Course 정보를 출력
    print_course_summary(course)

    # DB 업로드: 실패 시 전체 롤백되도록 단일 세션/트랜잭션 안에서 수행
    with get_db() as db:
        places = PlaceUpserter(db).upsert(course)
        print(f"Upserted {len(places)} place(s).")

        intervals = CourseIntervalUpserter(db).upsert(course, places)
        print(f"Upserted {len(intervals)} course interval(s).")


if __name__ == "__main__":
    main()
