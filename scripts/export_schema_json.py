import json
import os
import sys
from pathlib import Path

import django
from graphql import get_introspection_query

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sandbox.settings")
django.setup()

from sandbox.schema.dashboard import schema

query = get_introspection_query(
    descriptions=True,
    specified_by_url=True,
    directive_is_repeatable=True,
)

result = schema.execute_sync(query)

if result.errors:
    raise RuntimeError(result.errors)


with open("schema.json", "w", encoding="utf-8") as f:
    json.dump(
        {"data": result.data},
        f,
        ensure_ascii=False,
        indent=2,
    )
