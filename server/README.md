# Trailine Server

Trailine 서비스의 백엔드 서버입니다. 이 프로젝트는 모노레포로 구성되어 있으며, 관리자 페이지, API 서버, 공용 데이터 모델 라이브러리를 포함하고 있습니다.

## 🚀 프로젝트 구조

이 프로젝트는 `uv/pyproject`를 사용한 모노레포로 구성되어 있습니다. 각 패키지의 역할은 다음과 같습니다.

```
/
│── admin/      # 관리자 페이지 (Admin Dashboard)
│── api/        # 메인 API 서버
│── model/      # 데이터베이스 ORM Model (공용 라이브ar리)
└── pyproject.toml
```

*   **`admin`**: 서비스 관리를 위한 SQLAdmin+Web 기반의 관리자 페이지입니다.
*   **`api`**: 핵심 API 서버입니다.
*   **`model`**: `api`와 `admin` 등 여러 패키지에서 공통으로 사용하는 데이터베이스 모델 및 관련 유틸리티를 포함하는 라이브러리입니다.

## ✨ 기술 스택

* **`api`**:
  * FastAPI
  * sqlalchemy
  * pytest
* **`admin`**:
  * SQLAdmin
  * sqlalchemy
* **`model`**:
  * SQLAdmin

## Docs

각 레포 마다 README.md가 있으며, 여기서 직접 링크를 통해 문서를 확인하실 수 있습니다.

* [api](./api/README.md)
* [model](./model/README.md)
* [admin](./admin/README.md)
