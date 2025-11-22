import os
from uuid import uuid4

import boto3
from botocore.exceptions import NoCredentialsError
from mypy_boto3_s3 import S3Client
from fastapi import UploadFile, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from .config import config


def upload_image_to_s3(image :UploadFile, base_path: str, dirpath: str) -> str:
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

    # s3 업로드 설정
    s3_client: S3Client = boto3.client("s3")

    # 파일 확장자 및 새로운 파일명 생성
    _, ext = os.path.splitext(image.filename)
    new_filename = f"{uuid4()}{ext}"
    s3_path = f"{base_path}/{dirpath}/{new_filename}"

    try:
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

    return f"{config.S3.IMAGE_PUBLIC_BASE_URL}/{s3_path}"