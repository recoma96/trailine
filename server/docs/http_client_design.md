# 외부 API 클라이언트 설계 및 httpx.AsyncClient 활용 가이드

이 문서는 프로젝트 내에서 외부 API와 통신하기 위해 구현된 `ExternalAPIClient`의 설계 의도와 `httpx.AsyncClient`의 기술적 특성을 기록합니다.

---

## 1. 기술 파트: 왜 httpx.AsyncClient를 재사용해야 하는가?

### 1.1. 연결 생성 비용 (Connection Overhead)
HTTP 통신, 특히 HTTPS 통신은 단순히 데이터를 주고받는 것 이상의 비용이 발생합니다.
*   **TCP 3-Way Handshake**: 서버와 연결을 맺기 위해 패킷을 3번 주고받아야 합니다.
*   **TLS/SSL Handshake**: 보안 연결을 위해 인증서 교환 및 암호화 키 합의 과정이 추가로 발생하며, 이는 수차례의 네트워크 왕복(Round-trip)을 필요로 합니다.
*   **재사용의 이점**: 클라이언트를 재사용하면 이미 연결된 선로(Keep-Alive)를 그대로 사용하므로, 위 과정이 생략되어 응답 속도가 비약적으로 향상됩니다.

### 1.2. 운영체제 리소스 관리 (Socket Exhaustion)
*   클라이언트를 생성하고 요청 후 즉시 닫으면, 해당 소켓은 OS 수준에서 바로 해제되지 않고 `TIME_WAIT` 상태로 남습니다.
*   짧은 시간에 많은 요청이 발생할 경우, 가용 소켓이 고갈되어 새로운 연결을 맺을 수 없는 `OS Error`가 발생할 수 있습니다.
*   **Connection Pooling**: `AsyncClient`를 공유하면 내부적으로 소켓 풀을 관리하여 불필요한 소켓 생성을 방지합니다.

---

## 2. 설계 파트: ExternalAPIClient의 구현 전략

### 2.1. 의존성 주입 (Dependency Injection)을 통한 관리
`ExternalAPIClient`는 `httpx.AsyncClient`를 내부에서 직접 생성하기보다 외부에서 주입받는 방식을 권장합니다.

*   **중앙 집중식 설정**: `container.py`에서 타임아웃, 커넥션 풀 크기 등을 한 번에 설정할 수 있습니다.
*   **테스트 용이성**: 실제 네트워크 통신 대신 Mock 클라이언트를 주입하여 비즈니스 로직만 독립적으로 테스트할 수 있습니다.
*   **유연한 확장**: 특정 API는 다른 설정(예: 인증 헤더가 고정된 클라이언트)이 필요할 때, 별도의 클라이언트 인스턴스를 주입하기 쉽습니다.

### 2.2. 응답 처리 모델 (ExternalApiResponse)
성공과 실패를 명확히 구분하기 위해 `ExternalApiResponse` 객체를 반환합니다.

*   **is_success**: 상태 코드가 2xx인지 여부를 즉시 확인 가능합니다.
*   **TypeAdapter 지원**: Pydantic의 `TypeAdapter`를 내부적으로 사용하여 단일 객체 뿐만 아니라 **JSON List(`[...]`) 형태의 응답**도 `List[MyModel]` 형식으로 안전하게 파싱할 수 있습니다.
*   **Generic Support**: 성공/실패 시 각각 다른 형식을 사용하여 타입을 안전하게 보장받을 수 있습니다.
*   **Raw Data 접근**: 파싱된 데이터(`data`)뿐만 아니라, 로깅이나 디버깅을 위해 원본 데이터(`raw_body`)를 함께 보관합니다.

### 2.3. 요청 바디의 유연성
*   **Dict 기반 Body**: `BaseModel` 상속을 강제하지 않고 `dict`를 기본으로 받아 가독성과 자유도를 높였습니다.
*   **Multipart/Form 지원**: `is_form` 플래그를 통해 JSON 요청과 Form 요청을 쉽게 전환할 수 있습니다.

---

## 3. 사용 예시 (Best Practice)

### Dependency Injection 설정
```python
# container.py
class Container(containers.DeclarativeContainer):
    # 공통 클라이언트 (Singleton 권장)
    http_client = providers.Resource(httpx.AsyncClient, timeout=30.0)

    # 서비스별 API 클라이언트
    weather_api = providers.Factory(
        ExternalAPIClient,
        client=http_client,
        base_url="https://api.weather.go.kr"
    )
```

### 서비스 레이어 사용
```python
async def get_weather(self):
    response = await self.weather_api.request("GET", "/forecast")
    if response.is_success:
        return response.data  # 파싱된 데이터 사용
    else:
        logger.error(f"Error {response.status_code}: {response.error_msg}")
```
