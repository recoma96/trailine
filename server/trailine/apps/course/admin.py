from django.contrib import admin
from django.utils.html import format_html

from .forms import AdminCourseSeriesImageForm
from .models import CourseSeries, CourseSeriesImage


class CourseSeriesImageInline(admin.TabularInline):
    """CourseSeriesImage 모델을 CourseSeries 어드민 페이지에서 인라인으로 관리하기 위한 클래스"""

    model = CourseSeriesImage
    extra = 1  # 기본으로 보여줄 추가 빈 폼의 수
    verbose_name = "코스 시리즈 이미지"
    verbose_name_plural = "코스 시리즈 이미지들"
    readonly_fields = ("thumb",)

    @admin.display(description="이미지 미리보기", empty_value="이미지 없음")
    def thumb(self, obj: CourseSeriesImage):
        if obj.image:
            return format_html('<img src="{}" style="max-height:250px" />', obj.image.url)
        return None


@admin.register(CourseSeries)
class CourseSeriesAdmin(admin.ModelAdmin):
    """CourseSeries 모델을 위한 어드민 설정"""

    list_display = ("id", "title", "description", "created_at", "updated_at")
    search_fields = ("title",)
    inlines = [CourseSeriesImageInline]
    ordering = ("-id",)


@admin.register(CourseSeriesImage)
class CourseSeriesImageAdmin(admin.ModelAdmin):
    """CourseSeriesImage 모델을 위한 어드민 설정"""
    form = AdminCourseSeriesImageForm
    list_display = ("id", "course_series", "thumb", "created_at")
    list_select_related = ("course_series",)  # ForeignKey 필드 성능 최적화
    search_fields = ("course_series__title",)

    @admin.display(description="이미지 미리보기", empty_value="이미지 없음")
    def thumb(self, obj: CourseSeriesImage):
        if obj.image:
            return format_html('<img src="{}" style="max-height:250px" />', obj.image.url)
        return None
