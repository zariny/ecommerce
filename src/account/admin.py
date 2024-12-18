from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from . import models



@admin.register(models.User)
class UserAdmin(AuthUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {
            "fields": ("is_active", "is_confirmed", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Dates", {"fields": ("last_login",)})
    )

    add_fieldsets = (
        (
            None,
            {"classes": ("wide",), "fields": ("email", "usable_password", "password1", "password2"),}
        ),
    )

    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "is_staff")

