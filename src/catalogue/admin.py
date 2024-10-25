from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from .models import Category, CategoryTranslation


class IsPublicFilter(admin.SimpleListFilter):
    title = "Public status"
    parameter_name = "is_public"

    def lookups(self, request, model_admin):
        return [
            ('true', 'Public'),
            ('false', 'Non-Public'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(is_public=True)
        elif self.value() == 'false':
            return queryset.filter(is_public=False)


@admin.register(Category)
class CategoryAdmin(TreeAdmin):
    form = movenodeform_factory(Category)
    list_filter = (IsPublicFilter,)

    fieldsets = (
        ("Overview", {
            'fields': (
                'name',
                'slug',
                'description',
                'meta_title',
                'meta_description',
                'is_public',
                'ancestors_are_public'
            )
        }),
        ('Background', {
            'fields': (
                'background',
                'background_caption',
            )
        }),
        ('Tree Structure', {
            'fields': (
                '_position',
                '_ref_node_id'
            )
        }),
    )

    prepopulated_fields = {"slug": ("name",)}


admin.site.register(CategoryTranslation)
