from trailine.apps.common.types import CustomEnumType


class AuthRequestPurpose(CustomEnumType):
    SIGNUP = "signup"
    PASSWORD_CHANGE = "password-change"
