from smtplib import SMTPException

from django.core.cache import cache
from django.core.mail import send_mail

from trailine.apps.api.v1.auth.utils import (
    generate_verification_code,
    get_verify_cache_key
)
from trailine.apps.common.exc import EmailSendFailed


def send_verify_email(purpose: str, target_email: str):
    VERIFICATION_TIMEOUT = 300
    verification_code = generate_verification_code()

    try:
        success_count = send_mail(
            "[트레일라인] 이메일 인증 코드입니다.",
            f"인증 코드: {verification_code}",
            from_email=None,
            recipient_list=[target_email],
            fail_silently=False,
        )
    except SMTPException:
        raise EmailSendFailed

    if success_count != 1:
        raise EmailSendFailed

    cache_key = get_verify_cache_key(purpose, target_email)
    cache.set(
        cache_key,
        verification_code,
        timeout=VERIFICATION_TIMEOUT
    )

    return verification_code
