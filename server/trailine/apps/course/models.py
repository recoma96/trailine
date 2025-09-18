from django.db import models

from trailine.apps.common.models import TimeStampModel


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
    url = models.URLField(max_length=512, verbose_name="URL", help_text="URL")
