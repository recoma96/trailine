from django.contrib import admin

from trailine.apps.privacy_terms.models import PrivacyTerm, PrivacyTermVersion


class PrivacyTermVersionInline(admin.TabularInline):
    model = PrivacyTermVersion
    extra = 1
    ordering = ("-version",)


class PrivacyTermAdmin(admin.ModelAdmin):
    list_display = ("name", "get_version", "created_at", "updated_at")
    search_fields = ("name",)
    model = PrivacyTerm
    inlines = (
        PrivacyTermVersionInline,
    )

    @admin.display(description="최신버전")
    def get_version(self, obj: PrivacyTerm) -> int:
        return (PrivacyTermVersion.objects.filter(privacy_term=obj)
                .order_by("-version").values_list("version", flat=True).first())


admin.site.register(PrivacyTerm, PrivacyTermAdmin)
