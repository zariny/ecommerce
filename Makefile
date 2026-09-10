.DEFAULT_GOAL := help
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

MANAGE := uv run sandbox/manage.py
APP ?=
IMAGE_NAME ?= ecommerce
IMAGE_TAG ?= latest

.PHONY: help dev runserver check mm migrate superuser shell test \
	sync_permissions staticfiles up env schema json-schema erd \
	docs docs-build image container-run

## Development
dev: ## Run uvicorn with auto reload
	uv run uvicorn sandbox.asgi:application --reload

runserver: ## Run Django development server
	$(MANAGE) runserver

## Database
mm: ## Create migrations (APP=users)
	$(MANAGE) makemigrations $(APP)

migrate: ## Apply migrations
	$(MANAGE) migrate

## Django
check: ## Run Django system checks
	$(MANAGE) check

shell: ## Open Django shell
	$(MANAGE) shell

superuser: ## Create Django superuser
	$(MANAGE) createsuperuser

test: ## Run tests
	$(MANAGE) test

sync_permissions: ## Sync custom permissions
	$(MANAGE) sync_permissions

staticfiles: ## Collect static files
	$(MANAGE) collectstatic

## Utilities
up: env dev ## Prepare .env and run dev server
	@echo "⚠️  development environment"

env: ## Create .env from .env.example if missing
	@test -f .env || cp .env.example .env
	@echo "⚠️  dummy .env file is ready."

schema: ## Export GraphQL schema
	$(MANAGE) export_schema sandbox.schema.dashboard:schema > docs/graphql/schema.graphql

json-schema: schema ## Convert schema to introspection JSON
	uv run scripts/schema_to_introspection.py docs/graphql/schema.graphql docs/graphql/schema.json

erd: ## Generate ERD diagram
	$(MANAGE) generate_erd -d mermaid -o docs/models/erd.mmd

## Docs
docs: json-schema erd ## Serve docs locally
	uv run --group docs mkdocs serve

docs-build: json-schema erd ## Build static docs
	uv run --group docs mkdocs build

## Docker
image: ## Build docker image
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

container-run: env ## Run docker container
	docker run \
		--name ecommerce-backend \
		--env-file .env \
		-e DEBUG=False \
		-p 8000:8000 \
		$(IMAGE_NAME):$(IMAGE_TAG)

## Help
help: ## Show this help
	@echo ""
	@echo "Usage:"
	@echo "  make <target> [APP=app_name]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  %-18s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""