# trailine

등산 및 트레킹 코스에 대한 가이드를 알려주는 서비스 [릴리즈 노트](https://github.com/recoma96/trailine/releases)


## Demo Screenshots

![](docs/imgs/readme-1.png)
![](docs/imgs/readme-2.png)
![](docs/imgs/readme-3.png)


* * *

## 개발 목표

* 코스 길이, 난이도, 일주일 날시, 주의사항 등 최대한 상세하게 알려줄 수 있다.
* GPS 기반으로 코스 인증이 된 유저에 한해 코스 이용 후가 작성
* 코스 여러개를 모아 원하는 코스집을 만들 수 있음


## 사용 기술

|포지션|사용기술|
|---|---|
|Backend|Python3.13, FastAPI, PostgreSQL, SQLAlchemy, SQLAdmin|
|Frontend(WEB)|Typescript, React, Astro, Tailwindcss|


## Repositories

현재 이 리포지토리는 단독으로 개발 및 운영되고 있기 때문에 메인 서비스와 관련된 프로젝트들은 이 하나의 리포 안에 관리되고 있습니다.

### 구성

* **[server](/server/README.md)**: Python / FastAPI 기반의 API 서버 프로젝트 입니다. 이 안에는 메인서버, DB모델, 관리자페이지 등이 있습니다.
* **[web](/web/README.md)**: Typescript / React / Astro 기반의 웹 프로젝트 입니다.
* nginx: 프록시 설정 관련 정보가 들어있습니다.


## Installation As Docker

개발 및 테스트용으로 Docker Compose를 통해 풀스택 형식으로 서비스를 실행할 수 있습니다.


0. Docker, Docker Compose 설치 필요
1. server 디렉토리에 들어가서 `.local.env`라는 환경변수 파일에 서버 빌드에 필요한 환경변수를 입력합니다.

```dotenv
DB_HOST=
DB_PORT=
DB_USER=
DB_PSWD=
DB_SCHEMA=
```

2. web 디렉토리에 들어가서 `.local.env`라는 환경변수 파일에 클라이언트 빌드에 필요한 환경변수를 입력합니다.

```dotenv
NAVER_MAPS_API_CLIENT=<Naver Maps Client Key>
```

3. (선택) 최상위루트에 `.env` 파일을 추가하고, 아래와 같이 입력합니다. 

```dotenv
DOCKER_NETWORK_NAME=<데이터베이스가 속해 있는 Docker Network 이름>
```

4. 아래와 같이 실행합니다.

```shell
docker compose -f 'docker-compose-local.yaml' up -d --build 
```
