.PHONY: help


help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  build     Builds the container"

build:
	docker build -t steffenmllr/docker-postgres-azure-backup .

run:
	docker run -it steffenmllr/docker-postgres-azure-backup /bin/bash

test:
	AZURE_ACCOUNT_NAME="XXXX" \
	AZURE_ACCOUNT_KEY="XXXX" \
	AZURE_SHARE_NAME='XXXX' \
	SLACK_URL="XXXX" \
	PGHOST="localhost" \
	PGPORT="5432" \
	PGUSER="XXXX" \
	PGPASSWORD="XXXX" \
	PGDATABASE="netze_development" \
	python run.py

