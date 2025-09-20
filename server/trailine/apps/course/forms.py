from django import forms

from trailine.apps.course.models import CourseSeriesImage


class AdminCourseSeriesImageForm(forms.ModelForm):
    class Meta:
        model = CourseSeriesImage
        fields = "__all__"
        widgets = {
            # 드래그&드롭/미리보기 있는 서드파티 위젯 안 쓰면 기본 ClearableFileInput
            "image": forms.ClearableFileInput(attrs={"accept": "image/"})
        }
