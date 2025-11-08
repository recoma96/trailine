from uvicorn import run
from dotenv import load_dotenv


load_dotenv()


def main() -> None:
    run("admin.main:app", host="127.0.0.1", port=8081, reload=True)
