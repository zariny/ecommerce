from django.db import models

"""List of all languages supported"""


class Language(models.TextChoices):
    EN = "en", "English"
    FA = "fa", "Persian"
    FR = "fr", "French"
    DE = "de", "German"
    AR = "ar", "Arabic"
