from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import CourseSeries, CourseSeriesImage


class CourseSeriesImageInline(admin.TabularInline):
    """CourseSeriesImage 모델을 CourseSeries 어드민 페이지에서 인라인으로 관리하기 위한 클래스"""

    model = CourseSeriesImage
    extra = 1  # 기본으로 보여줄 추가 빈 폼의 수
    verbose_name = "코스 시리즈 이미지"
    verbose_name_plural = "코스 시리즈 이미지들"


@admin.register(CourseSeries)
class CourseSeriesAdmin(admin.ModelAdmin):
    """CourseSeries 모델을 위한 어드민 설정"""

    list_display = ("id", "title", "description", "created_at", "updated_at")
    search_fields = ("title",)
    inlines = [CourseSeriesImageInline]


@admin.register(CourseSeriesImage)
class CourseSeriesImageAdmin(admin.ModelAdmin):
    """CourseSeriesImage 모델을 위한 어드민 설정"""

    list_display = ("id", "course_series", "url", "created_at")
    list_select_related = ("course_series",)  # ForeignKey 필드 성능 최적화
    search_fields = ("course_series__title",)
