import os
import re
from io import BytesIO
from typing import BinaryIO, Tuple
from uuid import uuid4

import boto3
from botocore.exceptions import NoCredentialsError
from geoalchemy2 import WKTElement
from mypy_boto3_s3 import S3Client
from fastapi import UploadFile, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from PIL import Image, ImageOps

from .config import config


def resize_image_file(upload_file: BinaryIO, max_length: int) -> BytesIO:
    """
    파일 크기를 리사이징 하는 함수

    :param upload_file: 리사이징 대상 이미지 파일, API로부터 받는 경우도 있기 때문에 file이 아닌, BinaryIO 형태로 받는다
    :param max_length: 최대 길이

    :return: 리사이징 된 바이너리 데이터
    """
    def _compute_target_size_by_long_edge(src_w: int, src_h: int, _max_length: int) -> Tuple[int, int]:
        if src_w <= 0 or src_h <= 0:
            raise ValueError("Image Resizing Error: Invalid source size")
        long_length = max(src_w, src_h)

        if long_length <= _max_length:
            return src_w, src_h

        ratio = _max_length / long_length
        dst_w = max(1, int(round(src_w * ratio)))
        dst_h = max(1, int(round(src_h * ratio)))
        return dst_w, dst_h


    upload_file.seek(0)

    with Image.open(upload_file) as im:
        # EXIF 회전 보정 (스마트폰 사진 필수)
        im = ImageOps.exif_transpose(im)

        src_width, src_height = im.size

        # target_size 계산
        dst_width, dst_height = _compute_target_size_by_long_edge(src_width, src_height, max_length)

        # 리사이즈 진행
        resized_im = im.resize((dst_width, dst_height), Image.Resampling.LANCZOS)

        # 포맷 유지
        output_format = im.format

        # 메모리 버퍼 생성
        buffer = BytesIO()

        # 포맷별 저장 옵션
        save_kwargs = {}

        if output_format == "JPEG":
            # JPEG는 알파 불가
            resized_im = resized_im.convert("RGB")
            save_kwargs.update(
                quality=85,
                optimize=True,
                progressive=True,
            )
        elif output_format == "PNG":
            save_kwargs.update(
                optimize=True,
                compress_level=9,
            )
        elif output_format == "WEBP":
            save_kwargs.update(
                quality=85,
                method=6,
            )
        else: # Defualt Format PNG
            output_format = "PNG"
            resized_im = resized_im.convert("RGBA")

        # BytesIO 에 저장
        resized_im.save(buffer, format=output_format, **save_kwargs)

        # 버퍼를 맨 처음으로 돌리기
        buffer.seek(0)

        return buffer



def upload_image_to_s3(image: UploadFile, base_path: str, dirpath: str) -> str:
    # 이미지가 첨부되었는지, 이미지 파일이 맞는 지 확인한다
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

    # 리사이징
    resized_file = resize_image_file(image.file, config.IMAGE_MAX_LENGTH)

    # s3 업로드 설정
    s3_client: S3Client = boto3.client("s3")

    # 파일 확장자 및 새로운 파일명 생성
    _, ext = os.path.splitext(image.filename)
    new_filename = f"{uuid4()}{ext}"
    s3_path = f"{base_path}/{dirpath}/{new_filename}"

    try:
        s3_client.upload_fileobj(
            resized_file,
            config.S3.BUCKET_NAME,
            s3_path,
            ExtraArgs={"ContentType": image.content_type},
        )
    except NoCredentialsError:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AWS 자격 증명 정보를 찾을 수 없습니다."
        )

    return f"{config.S3.IMAGE_PUBLIC_BASE_URL}/{s3_path}"


def parse_string_to_lat_lng(s: str) -> Tuple[float, float]:
    match = re.match(r"^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$", s)
    if not match:
        raise ValueError("Parsing Lat/Lng failed")
    lat, lon = match.groups()
    return float(lat), float(lon)


def parse_location_to_wkt(lat: float, lon: float) -> WKTElement:
    wkt_point = f"POINT({lon} {lat})"
    return WKTElement(wkt_point, srid=4326)
