# Aegis Gateway – Secure LLM Reverse Proxy

Aegis Gateway provides a security layer in front of LLM APIs.
It inspects prompts for secrets, PII, and injection patterns before forwarding them to an upstream model (e.g., Ollama).

This repository contains two services:

- **Gateway** – .NET 10 + YARP reverse proxy  
- **Inspection Service** – Python + FastAPI for prompt analysis  

Both run locally via Docker Compose.

---

## Requirements

To run everything via Docker Compose:

- **Docker** (Desktop or Engine)  
- **Docker Compose v2+**

Optional (for local development without containers):

- **.NET 10 SDK** – run/debug Gateway locally  
- **Python 3.11+** – run/debug Inspection Service locally  
- **Ollama** – only if you want to call a local CPU/GPU LLM  

---

## Run with Docker Compose

```bash
docker compose up --build
```

Services and ports:

| Service     | URL                   | Purpose                            |
|-------------|-----------------------|------------------------------------|
| inspection  | http://localhost:8000 | Rule-based prompt analysis         |
| gateway     | http://localhost:8080 | Reverse proxy with inspection step |

---

## Test the Inspection Service

```bash
curl -X POST http://localhost:8000/inspect -H "Content-Type: application/json" -d '{"prompt": "my key is AKIA123456789ABCDE"}'
```

Expected: at least one `secret_aws_access_key` finding.

---

## Test the Gateway

```bash
curl -X POST http://localhost:8080/api/generate -H "Content-Type: application/json" -d '{"model": "gpt-oss:20b", "prompt": "hello"}'
```

If the prompt is safe → forwarded to the LLM.  
If unsafe → returns `403` with findings.

---

## Environment Variables

### Gateway

Typical variables (e.g. from `docker-compose.yml`):

```yaml
PromptInspectionService__BaseAddress=http://inspection:8000
Yarp__Clusters__ollama__Destinations__primary__Address=http://host.docker.internal:11434/
ASPNETCORE_ENVIRONMENT=Development
```

### Inspection Service

```yaml
AEGIS_ML_APP_NAME=Aegis ML Inspection Service
AEGIS_ML_LOG_LEVEL=INFO
```

---

## Project Structure

```text
services/
  gateway/         # .NET reverse proxy (YARP)
  inspection/      # FastAPI-based prompt inspection
docker-compose.yml
```

---

## Tests

### Inspection Service

```bash
cd services/inspection
pytest
```

### Gateway

```bash
cd services/gateway
dotnet test
```
