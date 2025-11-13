import os
import re
import uuid
from typing import Any, List, Type
from markupsafe import Markup

import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import FastAPI, HTTPException
from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
from sqladmin import Admin, ModelView
from sqladmin.fields import FileField
from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from wtforms import StringField, Form

from trailine_model.base import engine
from trailine_model.models.course import CourseIntervalDifficulty
from trailine_model.models.place import Place, PlaceImage
from trailine_model.models.user import User

from .config import config


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
        Place.is_searchable,
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


class PlaceImageAdmin(ModelView, model=PlaceImage):
    # 'url' 필드를 파일 업로드 필드로 대체합니다.
    form_overrides = {"url": FileField}
    # 폼에서 'url' 필드의 라벨을 'Image'로 변경합니다.
    form_args = {
        "url": {
            "label": "Image"
        }
    }

    column_formatters = {
        # url 텍스트 대신 이미지 출력
        "url": lambda m, v: (
            Markup(f'<img src="{m.url}" style="max-height: 300px;">')
        ),
        "place_id": lambda m, v: f"{m.place_id} - {m.place.name}"
    }

    column_list = [
        PlaceImage.place,  # relationship을 로드하기 위해 추가
        PlaceImage.sort_order,
        PlaceImage.url,
    ]
    form_excluded_columns = [PlaceImage.created_at, PlaceImage.updated_at]

    async def on_model_change(
        self, data: dict, model: Any, is_created: bool, request: Request
    ) -> None:
        image: UploadFile = data.get("url")

        # 이미지가 첨부되었는지, 이미지 파일이 맞는지 확인합니다.
        if not image or not image.filename:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="이미지 파일이 필요합니다."
            )
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="이미지 파일만 업로드할 수 있습니다."
            )

        # S3 업로드 설정
        s3_client = boto3.client("s3")

        # 파일 확장자 및 새로운 파일명 생성
        _, ext = os.path.splitext(image.filename)
        new_filename = f"{uuid.uuid4()}{ext}"
        place_id = data.get("place")
        s3_path = f"{config.S3.BASE_PLACE_PATH}/{place_id}/images/{new_filename}"

        try:
            # S3에 파일 업로드
            s3_client.upload_fileobj(
                image.file,
                config.S3.BUCKET_NAME,
                s3_path,
                ExtraArgs={"ContentType": image.content_type},
            )
        except NoCredentialsError:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AWS 자격 증명 정보를 찾을 수 없습니다."
            )

        # 데이터베이스에 저장할 S3 URL 생성
        s3_url = f"{config.S3.IMAGE_PUBLIC_BASE_URL}/{s3_path}"
        data["url"] = s3_url


admin.add_view(UserAdmin)
admin.add_view(CourseIntervalDifficultyAdmin)
admin.add_view(PlaceAdmin)
admin.add_view(PlaceImageAdmin)
