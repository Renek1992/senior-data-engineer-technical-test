.PHONY: build up down shell reset-db set-permissions shell postgres-shell

# HOME := /opt/src/

# Logging helper
define log
	@echo "[$(shell date '+%Y-%m-%d %H:%M:%S')] $(1)"
endef


reset-db: down set-permissions
	$(call log,"Resetting database: removing db-data")
	@rm -rfv db-data

build: reset-db
	$(call log,"Building Docker containers with no cache")
	@docker compose down
	@docker compose build --no-cache

set-permissions:
	$(call log,"Setting permissions for db-data directory")
	@mkdir -p db-data
	@chmod -R 777 db-data

up: set-permissions
	$(call log,"Starting containers")
	@docker compose up -d

down:
	$(call log,"Stopping containers")
	@docker compose down

shell:
	$(call log,"Opening shell in core container")
	@docker compose exec core bash -c "cd /opt/src; exec bash"

postgres-shell:
	$(call log,"Opening shell in postgres container")
	@docker compose exec postgres bash