import re
from typing import Any, List, Type

from fastapi import FastAPI
from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
from sqladmin import Admin, ModelView
from starlette.requests import Request
from wtforms import StringField, Form

from trailine_model.base import engine
from trailine_model.models.course import CourseIntervalDifficulty
from trailine_model.models.place import Place
from trailine_model.models.user import User

app = FastAPI()
admin = Admin(app, engine)


class UserAdmin(ModelView, model=User):
    # 생성 및 수정 폼에서 created_at과 updated_at 필드를 제외합니다.
    form_excluded_columns = [User.created_at, User.updated_at]
    can_delete = False
    column_list = [
        User.id,
        User.email,
        User.nickname,
        User.is_active,
        User.can_access_admin,
        User.last_login_at,
        User.created_at,
        User.updated_at
    ]


class CourseIntervalDifficultyAdmin(ModelView, model=CourseIntervalDifficulty):
    form_excluded_columns = [
        CourseIntervalDifficulty.created_at,
        CourseIntervalDifficulty.updated_at
    ]
    column_list = [
        CourseIntervalDifficulty.id,
        CourseIntervalDifficulty.level,
        CourseIntervalDifficulty.code,
        CourseIntervalDifficulty.name,
        CourseIntervalDifficulty.created_at,
        CourseIntervalDifficulty.updated_at
    ]


class PlaceAdmin(ModelView, model=Place):
    column_list = [
        Place.id,
        Place.name,
        Place.road_address,
        Place.land_address,
        Place.geog,
        Place.created_at,
        Place.updated_at,
    ]
    # 폼에서 geog와 geom 필드를 제외합니다.
    form_excluded_columns = [Place.geog, Place.geom, Place.created_at, Place.updated_at]

    # 폼을 동적으로 생성하고 'geo' 필드를 추가합니다.
    async def scaffold_form(self, rules: List[str] | None = None) -> Type[Form]:
        form = await super().scaffold_form()
        form.geo = StringField("Geo (Latitude,Longitude)")
        return form

    # 수정 화면에 기존 값을 미리 채워 넣습니다.
    async def on_form_prefill(self, form: Any, id: Any) -> None:
        model = await self.get_object_for_edit(id)
        if model and model.geog:
            point = to_shape(model.geog)
            # "위도,경도" 형식으로 변환합니다.
            form.geo.data = f"{point.y},{point.x}"

    # 모델 저장 직전에 데이터를 변환합니다.
    async def on_model_change(
        self, data: dict, model: Any, is_created: bool, request: Request
    ) -> None:
        geo_string = data.get("geo")
        if geo_string:
            # "위도,경도" 형식의 문자열을 파싱합니다.
            match = re.match(r"^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$", geo_string)
            if match:
                lat, lon = match.groups()
                # WKT POINT 형식(POINT(경도 위도))으로 변환합니다.
                wkt_point = f"POINT({lon} {lat})"
                point_element = WKTElement(wkt_point, srid=4326)
                # geog와 geom 필드에 동일한 값을 할당합니다.
                model.geog = point_element
                model.geom = point_element

        # 가상 필드인 'geo'는 모델에 저장하지 않으므로 data 딕셔너리에서 제거합니다.
        data.pop("geo", None)


admin.add_view(UserAdmin)
admin.add_view(CourseIntervalDifficultyAdmin)
admin.add_view(PlaceAdmin)
