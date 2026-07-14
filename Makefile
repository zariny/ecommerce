MANAGE := uv run sandbox/manage.py


dev:
	$(MANAGE) runserver

check:
	$(MANAGE) check

mm:
	$(MANAGE) makemigrations $(APP)

migrate:
	$(MANAGE) migrate

superuser:
	$(MANAGE) createsuperuser

shell:
	$(MANAGE) shell

help:
	@echo ""
	@echo "Available commands:"
	@echo "  make dev"
	@echo "  make check"
	@echo "  make migrate"
	@echo "  make mm APP=app_name"
	@echo "  make superuser"
	@echo "  make shell"
	@echo ""
