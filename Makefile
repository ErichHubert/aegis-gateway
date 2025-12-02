# Top-level Makefile for Aegis Gateway + Inspection Service

PYTHON ?= python3

INSPECTION_DIR := services/inspection
INSPECTION_VENV := $(INSPECTION_DIR)/.venv

GATEWAY_DIR := services/gateway
GATEWAY_PROJECT := Aegis.Gateway/Aegis.Gateway.csproj

INSPECTION_IMAGE := aegis-inspection:dev
GATEWAY_IMAGE := aegis-gateway:dev

.PHONY: help \
        inspection-venv inspection-deps inspection-test inspection-run inspection-docker-build inspection-docker-run \
        gateway-restore gateway-build gateway-test gateway-run gateway-docker-build gateway-docker-run \
        compose-up compose-down

help:
	@echo "Available targets:"
	@echo "  inspection-venv          Create virtualenv for inspection service"
	@echo "  inspection-deps          Install Python dependencies for inspection service"
	@echo "  inspection-test          Run Python tests for inspection service"
	@echo "  inspection-run           Run inspection service locally with uvicorn"
	@echo "  inspection-docker-build  Build inspection service Docker image"
	@echo "  inspection-docker-run    Run inspection service Docker container"
	@echo ""
	@echo "  gateway-restore          dotnet restore for gateway"
	@echo "  gateway-build            dotnet build for gateway"
	@echo "  gateway-test             dotnet test for gateway"
	@echo "  gateway-run              dotnet run gateway locally"
	@echo "  gateway-docker-build     Build gateway Docker image"
	@echo "  gateway-docker-run       Run gateway Docker container (expects network and inspection)"
	@echo ""
	@echo "  compose-up               docker compose up --build"
	@echo "  compose-down             docker compose down -v"

############################
# Inspection Service Targets
############################

inspection-venv:
	test -d $(INSPECTION_VENV) || (cd $(INSPECTION_DIR) && $(PYTHON) -m venv .venv)

inspection-deps: inspection-venv
	cd $(INSPECTION_DIR) && .venv/bin/pip install --upgrade pip && .venv/bin/pip install -r requirements.txt

inspection-test: inspection-deps
	cd $(INSPECTION_DIR) && PYTHONPATH=. .venv/bin/pytest

inspection-run: inspection-deps
	cd $(INSPECTION_DIR) && .venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --reload

inspection-docker-build:
	docker build -t $(INSPECTION_IMAGE) $(INSPECTION_DIR)

inspection-docker-run:
	docker run --rm \
		-p 8000:8000 \
		--name aegis-inspection \
		$(INSPECTION_IMAGE)

#####################
# Gateway Targets
#####################

gateway-restore:
	cd $(GATEWAY_DIR) && dotnet restore $(GATEWAY_PROJECT)

gateway-build: gateway-restore
	cd $(GATEWAY_DIR) && dotnet build $(GATEWAY_PROJECT) -c Debug

gateway-test:
	cd $(GATEWAY_DIR) && dotnet test

gateway-run:
	cd $(GATEWAY_DIR)/Aegis.Gateway && dotnet run

gateway-docker-build:
	docker build -t $(GATEWAY_IMAGE) $(GATEWAY_DIR)

# Note:
# - Expects a network named 'aegis-net' and a container 'aegis-inspection' in the same network
#   (or you adjust PromptInspectionService__BaseAddress accordingly).
gateway-docker-run:
	docker run --rm \
		--name aegis-gateway \
		--network aegis-net \
		-p 8080:8080 \
		-e ASPNETCORE_ENVIRONMENT=Development \
		-e PromptInspectionService__BaseAddress=http://aegis-inspection:8000 \
		$(GATEWAY_IMAGE)

#####################
# Docker Compose
#####################

compose-up:
	docker compose up --build

compose-down:
	docker compose down -v