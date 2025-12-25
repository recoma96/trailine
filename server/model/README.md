# Trailine DB Model

API서버와 Admin에서 공용으로 사용하는 DB Model 라이브러리 입니다. [api](/server/api/README.md)와 [admin](/server/admin/README.md)이 공통으로 사용하는 DB ORM 라이브러리 입니다.


## Installation

### 환경변수 설정

`server/model/.env`

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

server $ source .venv/bin/activate

(venv) server $ cd model
```

### 마이그레이션

```shell
(venv) server/model $ alembic upgrade head
```

### 모델 추가 및 생성 시

```shell
(venv) server/model $ alembic revision autogenerate -m "{메세지}"
```
