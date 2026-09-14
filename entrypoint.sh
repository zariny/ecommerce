#!/bin/sh
set -e

echo "PORT=$PORT"
echo "Starting server in background so the port opens immediately..."
uvicorn sandbox.asgi:application --host 0.0.0.0 --port "${PORT:-8000}" --log-level debug --access-log &
SERVER_PID=$!

echo "Running migrations..."
python sandbox/manage.py migrate --noinput

echo "Sync Enum permission..."
python sandbox/manage.py sync_permissions

echo "Collect static files..."
python sandbox/manage.py collectstatic --noinput

if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Creating superuser if needed..."
  python sandbox/manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser(
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD',
    )
"
fi

echo "Setup finished, handing over to server process..."
wait $SERVER_PID