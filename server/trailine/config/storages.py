from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class CustomS3Storage(S3Boto3Storage):
    """
    S3에 파일을 저장하기 위한 Custom Storage
    개발단의 경우 dev/ 안에 저장한다.
    """
    location = "dev" if settings.DEBUG else ""
    file_overwrite = False
