# Trailine Server


## Installation <작성중>

1. Python 3.13, uv 패키지 설치 필요
2. `uv` 를 이용해 패키지 설치
3. AWS configure 설정
4. 환경변수 세팅
```dotenv
DJANGO_SECRET_KEY=<장고 시크릿키 (암의문자열)>

DB_HOST=
DB_NAME=
DB_PASSWORD=
DB_PORT=
DB_USER=

EMAIL_HOST_USER=<이메일 전송 호스트 이메일>
EMAIL_HOST_PASSWORD=<이메일 전송을 하기 위한 호스트 비밀번호>
DEFAULT_FROM_EMAIL=<송신 이메일 정보>

REDIS_HOST=
REDIS_PORT=
```

5. 개발서버 실행
```python
uv run manage.py runserver --settings=trailine.config.settings.development
```
