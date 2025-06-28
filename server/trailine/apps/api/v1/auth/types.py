from trailine.apps.common.types import CustomEnumType


class AuthRequestPurpose(CustomEnumType):
    SIGNUP = "SIGNUP"
    PASSWORD_CHANGE = "PASSWORD-CHANGE"
