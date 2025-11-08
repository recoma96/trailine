import os

from uvicorn import run
from dotenv import load_dotenv


load_dotenv()


if os.getenv("IS_TEST", False):
    os.environ["DB_SCHEMA"] = f"{os.getenv('DB_SCHEMA', '')}_test"


def main() -> None:
    run("trailine_api.main:app", host="127.0.0.1", port=8080, reload=True)
