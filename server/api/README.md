# API Server

Trailine API Server 입니다

## Installation

### 환경변수 설정

`server/api/.env`

```dotenv
DB_HOST=<호스트>
DB_PORT=5432
DB_USER=<아이디>
DB_PSWD=<패스워드>
DB_SCHEMA=<스키마이름>
```

```shell
server $ uv venv # 이미 했다면 패스

server $ uv pip install -e model # DB Model 모듈 설치

server $ uv pip install -e api # API 서버 설치

server $ source .venv/bin/activate

server $ cd api

server/api $ runserver
```

### 추가1) 테스트 코드 구동

`.env` 에서 아래 문구 추가
```dotenv
IS_TEST=1
```

```shell
server/api $ pytest
```

### 추가2) 타입 체크 방법

API Server에 한정해서 Python 타입 검증을 위해 `mypy`를 도입하고 있습니다. 사용 방법은 아래와 같습니다

```shell
server $ source .venv/bin/activate

(.ven)server $ cd api

(.venv)server $ mypy
```