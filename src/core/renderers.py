from rest_framework.renderers import JSONRenderer


class StructuredJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context is not None:
            has_exception = renderer_context["response"].exception
            status_code = renderer_context["response"].status_code
            success_flag: bool = not has_exception and status_code < 400
            default_massaage = "Succesfully" if success_flag else "Failed"
            if data:
                message: str = data.pop("detail", default_massaage)
            else:
                message: str = default_massaage
            data = {
                "success": success_flag,
                "message": message,
                "data": data if success_flag else None,
                "errors": data if not success_flag else None
            }
        return super().render(data, accepted_media_type, renderer_context)
