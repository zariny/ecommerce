.DEFAULT_GOAL := help

MANAGE := uv run sandbox/manage.py
APP ?=

.PHONY: help dev runserver check mm migrate superuser shell test env schema

## Development
dev:
	uv run uvicorn sandbox.asgi:application --reload

runserver:
	$(MANAGE) runserver

## Database
mm:
	$(MANAGE) makemigrations $(APP)

migrate:
	$(MANAGE) migrate

## Django
check:
	$(MANAGE) check

shell:
	$(MANAGE) shell

superuser:
	$(MANAGE) createsuperuser

test:
	$(MANAGE) test

## Utilities
env:
	@test -f .env || cp .env.example .env
	@echo "✅ .env is ready."

schema:
	$(MANAGE) export_schema sandbox.schema.dashboard:schema > schema.graphql

json-schema: schema
	uv run scripts/schema_to_introspection.py schema.graphql docs/schema.json

## Help
help:
	@echo ""
	@echo "Usage:"
	@echo "  make <target>"
	@echo ""
	@echo "Targets:"
	@printf "  %-15s %s\n" "dev" "Run uvicorn with auto reload"
	@printf "  %-15s %s\n" "runserver" "Run Django development server"
	@printf "  %-15s %s\n" "check" "Run Django system checks"
	@printf "  %-15s %s\n" "mm APP=users" "Create migrations"
	@printf "  %-15s %s\n" "migrate" "Apply migrations"
	@printf "  %-15s %s\n" "superuser" "Create Django superuser"
	@printf "  %-15s %s\n" "shell" "Open Django shell"
	@printf "  %-15s %s\n" "test" "Run tests"
	@printf "  %-15s %s\n" "schema" "Export GraphQL schema"
	@printf "  %-15s %s\n" "env" "Create .env from .env.example"
	@echo ""