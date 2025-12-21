import os
from typing import Callable

from uvicorn import run
from dotenv import load_dotenv


load_dotenv()


if os.getenv("IS_TEST", False):
    os.environ["DB_SCHEMA"] = f"{os.getenv('DB_SCHEMA', '')}_test"


def run_in_coding(): # 개발하면서 테스트를 할 때 (Docker사용 X)
    run(""
        "trailine_api.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )

def run_in_local(): # Docker사용 + 테스트
    run(
        "trailine_api.main:app",
        host="0.0.0.0",
        port=8080,

        # 워커 수
        workers=2,

        # 접근 제한
        limit_concurrency=10,  # 워커 하나는 최대 10개의 요청을 동시에 처리할 수 있다.
        limit_max_requests=10_000  # 누적 1만개의 요청을 처리했으면, 다른 worker로 교체하고 해당 worker는 재시작 -> 메모리 누적 누수 방지
    )

def run_in_prod(): # Docker 사용 + Production
    run(
        "trailine_api.main:app",
        host="0.0.0.0",
        port=8080,

        # Client IP/Protocol 캐치용
        proxy_headers=True,
        forwarded_allow_ips="*",

        # 워커 수
        workers=2,

        # 접근 제한
        limit_concurrency=100, # 워커 하나는 최대 100개의 요청을 동시에 처리할 수 있다.
        limit_max_requests=100_000 # 누적 10만개의 요청을 처리했으면, 다른 worker로 교체하고 해당 worker는 재시작 -> 메모리 누적 누수 방지
    )

def main() -> None:
    runners: dict[str, Callable[[], None]] = {
        "local": run_in_local,
        "prod": run_in_prod,
        "__default__": run_in_coding,
    }

    env = os.getenv("APP_ENV", "__default__")
    runners.get(env, runners["__default__"])()
