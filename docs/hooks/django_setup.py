import os
import sys

import django

sys.path.insert(0, ".")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sandbox.settings")
django.setup()
