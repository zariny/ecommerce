from django.core.checks import Error, register
from django.conf import settings


@register()
def check_middleware_order(app_configs, **kwargs):
    errors = []
    middleware = settings.MIDDLEWARE

    tracker = "middleware.tracker.UserActivityTracker"
    jwt_detection = "middleware.detection.JWTTokenDetection"

    if tracker in middleware:
        if jwt_detection not in middleware:
            errors.append(
                Error(
                    "Missing middleware: JWTTokenDetectionMiddleware must be added to settings.MIDDLEWARE",
                    id="traffic_load.E001",
                )
            )
        elif middleware.index(tracker) < middleware.index(jwt_detection):
            errors.append(
                Error(
                    "Invalid middleware order: JWTTokenDetectionMiddleware must appear "
                    "before UserActivityTrackerMiddleware in settings.MIDDLEWARE.",
                    id="traffic_load.E002",
                )
            )

    return errors
