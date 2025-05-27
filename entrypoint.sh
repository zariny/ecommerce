#!/bin/sh

# Run migrations
echo "Running migrations..."
python sandbox/manage.py migrate

# Create dummy data
echo "Creating dummy data..."
python sandbox/manage.py createdummydata

# Create superuser if it doesn't exist
echo "Creating superuser..."
python sandbox/manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
email = "${DJANGO_SUPERUSER_EMAIL}"
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email="${DJANGO_SUPERUSER_EMAIL}",
        password="${DJANGO_SUPERUSER_PASSWORD}"
    )
END

# Start server
#echo "Starting Django server..."
#exec python sandbox/manage.py runserver 0.0.0.0:8000
