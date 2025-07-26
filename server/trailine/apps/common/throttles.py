from rest_framework.throttling import AnonRateThrottle
from rest_framework.exceptions import Throttled


class AuthRequestRateThrottle(AnonRateThrottle):
    scope = "auth_request"


    def throttle_failure(self) -> Throttled:
        wait = int(self.wait())
        raise Throttled(detail={
            "errorMessage": "너무 많은 요청을 했어요.",
            "remainedSeconds": wait
        })
