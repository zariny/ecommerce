from rest_framework.renderers import JSONRenderer


class StructuredJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context is not None:
            response = renderer_context["response"]
            has_exception = response.exception
            status_code = response.status_code
            success_flag: bool = not has_exception and status_code < 400
            default_message = "Successfully" if success_flag else "Failed"

            # Ensure `data` is a dictionary before using `.pop()`
            data = data or {}

            message: str = data.pop("detail", default_message)
            structured_data = {
                "success": success_flag,
                "status": status_code,
                "message": message,
                "data": data if success_flag else None,
                "errors": data if not success_flag else None
            }

            return super().render(structured_data, accepted_media_type, renderer_context)

        return super().render(data, accepted_media_type, renderer_context)