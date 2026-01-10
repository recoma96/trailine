from typing import Dict, List

import factory.fuzzy
from faker import Faker

from trailine_model.models.course import (
    CourseInterval,
    CourseIntervalDifficulty,
    CourseDifficulty,
    CourseStyle,
    Course,
    CourseCourseInterval,
    CourseImage,
    CourseIntervalImage
)
from trailine_model.models.place import Place

# Faker 인스턴스를 생성하여 직접 사용합니다.
fake = Faker()


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = None                   # 테스트에서 주입
        sqlalchemy_session_persistence = "flush"    # flush/commit 옵션


class PlaceFactory(BaseFactory):
    class Meta:
        model = Place

    class Params:
        latitude = factory.fuzzy.FuzzyFloat(-90.0, 90.0)
        longitude = factory.fuzzy.FuzzyFloat(-180.0, 180.0)

    name = factory.LazyFunction(lambda: fake.user_name()[:16])
    geom = factory.LazyAttribute(lambda o: f"SRID=4326;POINT({o.longitude} {o.latitude})")
    geog = factory.LazyAttribute(lambda o: f"SRID=4326;POINT({o.longitude} {o.latitude})")
    description = factory.Faker("text")
    is_searchable = True


class CourseIntervalDifficultyFactory(BaseFactory):
    class Meta:
        model = CourseIntervalDifficulty

    code = factory.LazyFunction(lambda: fake.user_name()[:16])
    name = factory.LazyFunction(lambda: fake.name()[:16])
    level = factory.fuzzy.FuzzyInteger(1, 10)
    description = factory.Faker("sentence")


class CourseIntervalImageFactory(BaseFactory):
    class Meta:
        model = CourseIntervalImage

    sort_order = factory.fuzzy.FuzzyInteger(1)
    url = factory.Faker("image_url")
    title = factory.Faker("name")
    description = factory.Faker("sentence")


class CourseIntervalFactory(BaseFactory):
    class Meta:
        model = CourseInterval

    class Params:
        # [{lat: <float>, lon:<float>, ele: <int>}..] 형식의 입력을 위한 파라미터
        # 파라미터가 주어지지 않으면 기본값으로 아래 데이터를 사용합니다.
        points = factory.LazyFunction(lambda: [
            {"lat": 37.5665, "lon": 126.9780, "ele": 38},
            {"lat": 37.5660, "lon": 126.9790, "ele": 40},
            {"lat": 37.5655, "lon": 126.9800, "ele": 42},
        ])

    # points 파라미터를 기반으로 LINESTRING Z 형식의 WKT 문자열을 생성합니다.
    geom = factory.LazyAttribute(
        lambda o: f"SRID=4326;LINESTRING Z ({', '.join([f'{p["lon"]} {p["lat"]} {p["ele"]}' for p in o.points])})"
    )

    name = factory.LazyFunction(lambda: fake.name()[:16])
    description = factory.Faker("sentence")
    place_a = factory.SubFactory(PlaceFactory)
    place_b = factory.SubFactory(PlaceFactory)
    difficulty = factory.SubFactory(CourseIntervalDifficultyFactory)
    length_m = factory.fuzzy.FuzzyInteger(100, 1000)
    duration_ab_minutes = factory.fuzzy.FuzzyInteger(10, 60)
    duration_ba_minutes = factory.fuzzy.FuzzyInteger(10, 60)

    # CourseInterval 생성 시 CourseImage 2개를 함께 생성합니다.
    images = factory.List([factory.SubFactory(CourseIntervalImageFactory, sort_order=i+1) for i in range(2)])


class CourseDifficultyFactory(BaseFactory):
    class Meta:
        model = CourseDifficulty

    code = factory.LazyFunction(lambda: fake.user_name()[:16])
    name = factory.LazyFunction(lambda: fake.name()[:16])
    level = factory.fuzzy.FuzzyInteger(1, 10)
    description = factory.Faker("sentence")


class CourseStyleFactory(BaseFactory):
    class Meta:
        model = CourseStyle

    code = factory.LazyFunction(lambda: fake.user_name()[:16])
    name = factory.LazyFunction(lambda: fake.name()[:16])
    description = factory.Faker("sentence")


class CourseImageFactory(BaseFactory):
    class Meta:
        model = CourseImage

    sort_order = factory.fuzzy.FuzzyInteger(1)
    url = factory.Faker("image_url")
    title = factory.Faker("name")
    description = factory.Faker("sentence")
    course_id = factory.LazyFunction(lambda cid: cid)


class CourseFactory(BaseFactory):
    class Meta:
        model = Course

    name = factory.Faker("name")
    description = factory.Faker("sentence")
    course_difficulty = factory.SubFactory(CourseDifficultyFactory)
    course_style = factory.SubFactory(CourseStyleFactory)
    is_published = True

    @factory.post_generation
    def links(self, create, extracted: List[Dict], **kwargs):
        if not create:
            return

        if extracted is None:
            return

        for item in extracted:
            CourseCourseIntervalFactory(course=self, **item)


class CourseCourseIntervalFactory(BaseFactory):
    class Meta:
        model = CourseCourseInterval

    course = factory.SubFactory(CourseFactory)
    interval = factory.SubFactory(CourseIntervalFactory)
    position = factory.fuzzy.FuzzyInteger(1, 10)
    is_reversed = True
