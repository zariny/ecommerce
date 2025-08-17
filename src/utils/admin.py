from django.contrib import admin
import typing


class AbstractPieChartModelAdmin(admin.ModelAdmin):
    change_list_template = "pie_chart.html"

    @typing.final
    def changelist_view(self, request, extra_context=None):
        response =  super().changelist_view(request, extra_context=extra_context)
        if hasattr(response, "context_data"):
            extra_context = extra_context or {}
            extra_context['has_paramether'] = False
            if 'cl' in response.context_data:
                cl = response.context_data['cl']
                filtered_count = cl.result_count
                unfiltered_count = cl.full_result_count - cl.result_count
                if filtered_count and unfiltered_count:
                    extra_context['filtered_count'] = filtered_count
                    extra_context['unfiltered_count'] = unfiltered_count
                    extra_context['has_paramether'] = True

            response.context_data.update(extra_context)
        return response
