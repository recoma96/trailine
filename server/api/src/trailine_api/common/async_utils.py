import inspect
from typing import Awaitable, TypeVar

T = TypeVar("T")


async def await_if_needed(value: T | Awaitable[T]) -> T:
    """
    반환값이 동기/비동기 혼합 타입으로 선언된 경우를 안전하게 처리한다.

    배경:
    - 일부 라이브러리는 동일한 API를 동기/비동기에서 모두 제공한다.
    - 타입 스텁이 이를 반영해 `T | Awaitable[T]` 같은 union으로 선언되면,
      mypy는 "await 대상이 아닐 수도 있다"고 판단해 오류를 낸다.
    - 실제 런타임에서는 비동기 클라이언트가 항상 awaitable을 돌려주더라도
      타입 정보만으로는 구분이 불가능하다.

    해결:
    - runtime에서 `inspect.isawaitable`로 확인하고 await 가능한 경우에만 await.
    - 동기 값이면 그대로 반환한다.

    목적:
    - 런타임 동작은 그대로 유지하면서 mypy 오류를 제거한다.
    - 호출부에서는 항상 `await await_if_needed(...)` 형태로 통일한다.
    """
    if inspect.isawaitable(value):
        return await value
    return value
