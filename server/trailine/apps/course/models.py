import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

from trailine.apps.common.models import TimeStampModel


def image_upload_to(instance: "CourseSeriesImage", filename: str) -> str:
    base, ext = os.path.splitext(filename)
    return f"public/course-series/{instance.course_series.id}/{uuid.uuid4()}{ext}"


class CourseSeries(TimeStampModel):
    class Meta:
        db_table = "course_series"
        verbose_name = "코스 시리즈"
        verbose_name_plural = "트레킹/하이킹 코스 시리즈"

    id = models.AutoField(primary_key=True, verbose_name="고유아이디", help_text="고유아이디")
    title = models.CharField(max_length=64, null=False, verbose_name="시리즈명", help_text="시리즈명")
    description = models.TextField(null=True, blank=True, verbose_name="시리즈설명", help_text="시리즈설명")


class CourseSeriesImage(TimeStampModel):
    class Meta:
        db_table = "course_series_image"
        verbose_name = "코스 시리즈 이미지"
        verbose_name_plural = "코스 시리즈 이미지"

    id = models.AutoField(primary_key=True, verbose_name="고유아이디", help_text="고유아이디")
    course_series = models.ForeignKey(
        CourseSeries,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="코스 시리즈",
        help_text="코스 시리즈",
    )
    image = models.ImageField(
        upload_to=image_upload_to,
        max_length=512,
        null=False,
        blank=False,
        verbose_name="URL",
        help_text="URL",
        db_column="url",
    )

    def clean(self):
        # 이미지 업로드 전의 유효성 검사
        if self.image:
            if self.image.size > settings.MAXIMUM_IMAGE_SIZE:
                raise ValidationError(f"이미지 용량은 {settings.MAXIMUM_IMAGE_SIZE_TO_TEXT} 이하여야 합니다.")
            valid_exts = settings.AVAILABLE_IMAGE_EXISTS
            ext = os.path.splitext(self.image.name)[1].lower()
            if ext not in valid_exts:
                raise ValidationError(f"허용 확장자: {', '.join(sorted(valid_exts))}")
