# Trailine Admin

Trailine 어드민 페이지 입니다.

## Installation

### 환경변수 설정

`server/admin/.env`

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

server $ uv pip install -e admin # 관리자 페이지 시스템 설치

server $ cd admin

server/admin $ run-admin
```