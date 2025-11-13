import os

from dotenv import load_dotenv

load_dotenv()


class _CommonConfig:
    REGION = "ap-northeast-2"
    class S3:
        BUCKET_NAME = "project-trailine"
        IMAGE_PUBLIC_BASE_URL = f"https://project-trailine.s3.ap-northeast-2.amazonaws.com"


class _DevConfig(_CommonConfig):
    class S3(_CommonConfig.S3):
        BASE_PLACE_PATH = "dev/public/place"


class _ProdConfig(_CommonConfig):
    class S3(_CommonConfig.S3):
        BASE_PLACE_PATH = "public/place"


IS_TEST: bool = (os.getenv("IS_TEST") == "1")
config = _DevConfig if IS_TEST else _ProdConfig
