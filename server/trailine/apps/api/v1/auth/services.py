from smtplib import SMTPException

from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings

from trailine.apps.api.v1.auth.utils import (
    generate_verification_code,
    get_verify_email_cache_key
)
from trailine.apps.common.exc import EmailSendFailed, AuthCodeNotExist, AuthCodeNotMatched
from trailine.apps.common.utils import get_verify_success_email_cache_key


def send_verify_email(purpose: str, target_email: str):
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

    cache_key = get_verify_email_cache_key(purpose, target_email)
    cache.set(
        cache_key,
        verification_code,
        timeout=settings.EMAIL_VERIFICATION_TIMEOUT
    )

    return verification_code


def verify_email_code(purpose: str, target_email: str, code: str):
    cache_key = get_verify_email_cache_key(purpose, target_email)
    cached_code = cache.get(cache_key)

    if not cached_code:
        raise AuthCodeNotExist

    if code != cached_code:
        raise AuthCodeNotMatched

    cache.delete(cache_key)

    verify_success_cache_key = get_verify_success_email_cache_key(target_email, purpose)

    cache.set(
        verify_success_cache_key,
        1,
        timeout=settings.EMAIL_VERIFICATION_SUCCESS_TIMEOUT
    )
