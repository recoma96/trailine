from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from trailine.apps.common.models import TimeStampModel
from trailine.apps.privacy_terms.models import PrivacyTermVersion


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str, nickname: str, **extra_fields):
        if not email:
            raise ValueError('Uses must have an email address')
        user = self.model(
            email=email,
            nickname=nickname
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, nickname: str, **extra_fields):
        superuser = self.create_user(email, password, nickname)
        superuser.set_password(password)
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save(using=self._db)
        return superuser


class User(TimeStampModel, AbstractBaseUser, PermissionsMixin):
    class Meta:
        db_table = "user"
        verbose_name = "사용자"
        verbose_name_plural = "사용자"

    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
    )
    
    id = models.AutoField(primary_key=True, verbose_name="유저아이디", help_text="유저아이디")
    email = models.EmailField(max_length=256, null=False, blank=False, unique=True,
                              verbose_name="이메일", help_text="로그인 및 인증에 사용되는 이메일")
    nickname = models.CharField(max_length=32, null=False, blank=False,
                                verbose_name="닉네임", help_text="화면에 보여지는 이름")
    is_staff = models.BooleanField(null=False, blank=True, default=False,
                                   verbose_name="관리자여부", help_text="관리자 페이지에 접속할 수 있는 계정 여부")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True,
                              verbose_name="성별", help_text="M: 남, F: 여, null: 정하지 않음")
    birthday = models.CharField(max_length=8, null=True, blank=True, verbose_name="생일", help_text="생일")
    profile_image_url = models.CharField(max_length=256, null=True, blank=True,
                                         verbose_name="프로필이미지URL", help_text="프로필이미지URL")
    inactivated_at = models.DateTimeField(null=True, blank=True, verbose_name="탈톼날짜", help_text="탈퇴한 날짜")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]

    objects = UserManager()


class UserPrivacyTerm(TimeStampModel):
    class Meta:
        db_table = "user_privacy_term"
        verbose_name = "사용자개인정보동의항목"
        verbose_name_plural = "사용자 개인정보 동의 항목"
        
    id = models.AutoField(primary_key=True, verbose_name="고유아이디", help_text="고유 아이디")
    user = models.ForeignKey(User, db_column="user_id", on_delete=models.PROTECT, null=False, blank=False,
                             verbose_name="사용자", help_text="해당 약관과 관련된 사용자")
    privacy_term_version = models.ForeignKey(PrivacyTermVersion, db_column="privacy_term_version_id",
                                             on_delete=models.PROTECT, null=False, blank=False,
                                             verbose_name="약관항목", help_text="해당 유저와 관련된 약관 항목")
    is_agreed = models.BooleanField(null=False, blank=False, verbose_name="약관동의여부", help_text="약관 동의 여부")
    agreed_at = models.DateTimeField(null=True, blank=False,
                                     verbose_name="동의날짜", help_text="동의 날짜 (동의 거부시 null 처리)")
