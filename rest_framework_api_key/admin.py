import typing

from django.contrib import admin, messages

from ._helpers import generate_key
from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("user", "prefix", "created", "revoked")
    list_filter = ("created", "revoked")

    readonly_fields = ("get_api_key",)
    search_fields = ("user",)

    fieldsets = ((None, {"fields": ("user", "revoked", "get_api_key")}),)
    actions = ("make_revoked", )

    def get_readonly_fields(
        self, request, obj: APIKey = None
    ) -> typing.Tuple[str]:
        if obj is not None and obj.revoked:
            return self.readonly_fields + ("user", "revoked")
        return self.readonly_fields

    def get_api_key(self, obj: APIKey) -> str:
        if obj.pk:
            return 16 * "*"
        return "The API key will be generated when clicking 'Save'."

    get_api_key.short_description = "API key"

    def save_model(self, request, obj: APIKey, form, change):
        created = not obj.pk

        if created:
            generated_key, key_id = generate_key()
            obj.id = key_id

            obj.save()

            message = (
                "The API key for {} is: {}. "
                "Please store it somewhere safe: "
                "you will not be able to see it again."
            ).format(obj.user, generated_key)
            messages.add_message(request, messages.WARNING, message)
        else:
            obj.save()

    def make_revoked(self, request, queryset):
        queryset.update(revoked=True)

    make_revoked.short_description = "Revoke selected API Keys"
