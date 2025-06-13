from django.db import models

from trailine.apps.common.models import TimeStampModel


class PrivacyTerm(TimeStampModel):
    class Meta:
        db_table = "privacy_terms"
        verbose_name = "개인정보동의약관"
        verbose_name_plural = " 개인 정보 동의 약관"

    id = models.AutoField(primary_key=True, verbose_name="고유아이디", help_text="고유아이디")
    code = models.CharField(max_length=32, null=False, blank=False, unique=True,
                            verbose_name="약관고유코드", help_text="약관 고유 코드")
    name = models.CharField(max_length=64, null=False, blank=False,
                            verbose_name="약관명", help_text="약관 이름")

    def __str__(self):
        return f"[{self.code}] {self.name}"


class PrivacyTermVersion(TimeStampModel):
    class Meta:
        db_table = "privacy_term_version"
        verbose_name = "버전별개인정보동의약관"
        verbose_name_plural = "버전별 개인정보 동의약관"

    id = models.AutoField(primary_key=True, verbose_name="고유아이디", help_text="고유아이디")
    privacy_term = models.ForeignKey(PrivacyTerm, db_column="privacy_term_id", on_delete=models.PROTECT,
                                     null=False, blank=False,
                                     verbose_name="약관항목", help_text="약관 항목")
    version = models.PositiveSmallIntegerField(null=False, blank=False, default=1,
                                               verbose_name="약관버전", help_text="약관 버전")
    title = models.CharField(max_length=256, null=False, blank=False, verbose_name="약관제목", help_text="약관 제목")
    content = models.TextField(null=False, blank=False, verbose_name="약관내용", help_text="약관 내용")
    is_required = models.BooleanField(null=False, blank=False,
                                      verbose_name="필수여부", help_text="필수 여부 (false: 선택)")
