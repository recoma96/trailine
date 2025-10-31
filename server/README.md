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
```shell
uv run manage.py runserver --settings=trailine.config.settings.development
```

* 테스트코드 실행 및 coverage 확인
```shell
# coverage 이전 내역 삭제
uv run coverage erase

# 테스트 코드 실행
uv run coverage run manage.py test --settings=trailine.config.settings.testing

# coverage 결과 터미널에서 보기
uv run coverage report

# coverage 결과 html 파일로 보기
uv run coverage html # 해당 구문 실행 이후 htmlcov 디렉토리에서 index.html 열기
```