from django.apps import AppConfig


class TrafficLoadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'traffic_load'

    def ready(self):
        import traffic_load.checks
