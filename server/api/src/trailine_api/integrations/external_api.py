import logging
from typing import Any, Dict, Optional, Type, Union, List

import httpx
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class ExternalApiResponse:
    """외부 API 응답 결과를 담는 클래스"""
    def __init__(
        self,
        status_code: int,
        data: Union[Dict[str, Any], List[Any], Any, None] = None,
        raw_body: Any = None,
        error_msg: Optional[str] = None
    ):
        self.status_code = status_code
        self.data = data  # 파싱된 Pydantic 모델 혹은 dict/raw data
        self.raw_body = raw_body  # 파싱 전 원본 데이터
        self.error_msg = error_msg

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

class ExternalAPIClient:
    """
    HTTPX 기반의 외부 API 호출 클라이언트.
    성공/실패 응답을 선택적으로 Pydantic 모델로 파싱합니다.
    """

    def __init__(
        self,
        base_url: str = "",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
        client: Optional[httpx.AsyncClient] = None,
    ):
        self.base_url = base_url
        self.headers = headers or {}
        self.params = params or {}
        self.timeout = timeout
        self._client = client

    async def request(
        self,
        method: str,
        path: str,
        success_model: Optional[Type[BaseModel]] = None,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        is_form: bool = False,
        headers: Optional[Dict[str, str]] = None,
    ) -> ExternalApiResponse:
        """
        외부 API에 요청을 보내고 응답을 처리합니다.
        """
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        combined_headers = {**(headers or {}), **self.headers}
        combined_params = {**(params or {}), **self.params}

        request_kwargs: Dict[str, Any] = {
            "method": method,
            "url": url,
            "params": combined_params,
            "headers": combined_headers,
            "timeout": self.timeout,
        }

        if body:
            if is_form:
                request_kwargs["data"] = body
            else:
                request_kwargs["json"] = body

        if self._client:
            return await self._send_request(self._client, request_kwargs, success_model)
        
        async with httpx.AsyncClient() as client:
            return await self._send_request(client, request_kwargs, success_model)

    async def _send_request(self, client: httpx.AsyncClient, kwargs: Dict[str, Any], success_model: Optional[Type[BaseModel]]) -> ExternalApiResponse:
        try:
            response = await client.request(**kwargs)
            return self._handle_response(response, success_model)
        except httpx.HTTPError as e:
            logger.error(f"External API Request Failed: {str(e)}", extra={"url": kwargs.get("url")})
            return ExternalApiResponse(status_code=500, error_msg=str(e))

    def _handle_response(self, response: httpx.Response, success_model: Optional[Type[BaseModel]]) -> ExternalApiResponse:
        status_code = response.status_code
        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text

        if not success_model:
            return ExternalApiResponse(status_code=status_code, data=response_data, raw_body=response_data)

        try:
            # 리스트 응답인 경우 각 요소를 검증 및 변환
            if isinstance(response_data, list):
                parsed_data = [success_model.model_validate(item) for item in response_data]
                return ExternalApiResponse(
                    status_code=status_code, 
                    data=parsed_data,
                    raw_body=response_data
                )
            
            # 딕셔너리 응답인 경우 단일 객체 검증
            if isinstance(response_data, dict):
                parsed_data = success_model.model_validate(response_data)
                return ExternalApiResponse(
                    status_code=status_code, 
                    data=parsed_data,
                    raw_body=response_data
                )
        except ValidationError as e:
            logger.error(f"Schema Validation Error: {str(e)}")
            return ExternalApiResponse(
                status_code=status_code, 
                data=response_data, 
                raw_body=response_data, 
                error_msg=f"validation_error: {str(e)}"
            )
        
        return ExternalApiResponse(
            status_code=status_code, 
            data=response_data, 
            raw_body=response_data
        )
