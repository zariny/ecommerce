from django.shortcuts import render

# from sandbox import urls
from django.http import JsonResponse
from django.views.csrf import csrf_failure as default_csrf_failure

GRAPHQL_API_URLS = ("/graphql/", "/dashboard/graphql/")  # FIXME Single source of truth


def home(request):
    return render(request, template_name="utils/home.html")


def csrf_failure(request, reason=""):
    path = request.path
    if path.startswith(GRAPHQL_API_URLS):
        return JsonResponse(
            {
                "errors": [
                    {
                        "message": "CSRF verification failed.",
                        "extensions": {
                            "code": "CSRF_FAILED",
                            "reason": reason,
                        },
                    }
                ],
                "data": None,
            },
            status=403,
        )

    return default_csrf_failure(
        request,
        reason=reason,
    )
