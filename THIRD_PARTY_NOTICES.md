# Third-Party Notices

This project, **Aegis Gateway**, includes and depends on third-party open-source software components.
The respective licenses apply to those components and are provided by their authors/maintainers.

This document is provided for convenience and does not replace the original license texts.
Where possible, license files are included in the distributed packages or linked from upstream sources.

---

## Overview

**Aegis Gateway** consists of:
- A **.NET / YARP** reverse proxy gateway (Gateway Service)
- A **Python / FastAPI** inspection service (Inspection Service)
- Optional local demo infrastructure via Docker Compose (e.g., echo service / Ollama)

---

## Notable Third-Party Components

### .NET Gateway Service
- **YARP (Yet Another Reverse Proxy)** — used as the reverse proxy framework.
  - License: (verify in upstream repository; commonly MIT for many Microsoft OSS components)
- **ASP.NET Core / .NET Runtime & SDK**
  - License: provided by Microsoft with the respective base images and distributions

### Python Inspection Service
- **FastAPI** — web framework
  - License: MIT (verify in upstream)
- **Uvicorn** — ASGI server
  - License: BSD/MIT-style (verify in upstream)
- **Pydantic / pydantic-settings** — configuration and validation
  - License: MIT (verify in upstream)
- **Microsoft Presidio Analyzer** — PII detection framework
  - License: MIT (verify in upstream)
- **spaCy** — NLP engine used by Presidio (via spaCy NLP engine integration)
  - License: MIT (verify in upstream)
- **spaCy model `en_core_web_lg`** — language model used for English NLP
  - License: provided by the model authors (verify in upstream release metadata)
- **detect-secrets** — secret detection library
  - License: Apache-2.0 (verify in upstream)

> Note: The inspection service also depends on additional transitive Python packages (e.g., Starlette, AnyIO, etc.).
> Those packages are installed via `requirements.txt` and carry their own license terms.

---

## Docker Base Images (Local Development / Demo)

This repository’s Dockerfiles use official images, including (but not limited to):
- `mcr.microsoft.com/dotnet/aspnet` / `mcr.microsoft.com/dotnet/sdk`
- `python:<version>-slim`

These images contain additional components and license terms provided by their respective publishers.

---

## Portions Derived From Other Projects

### detect-secrets (test payload inspiration)
Some test payloads and/or test-case patterns used for validating secret detection behavior were **adapted** from the
`detect-secrets` project and modified to fit this repository’s test suite and contracts.

- Upstream project: `detect-secrets`
- License: Apache-2.0
- Modifications: Adapted payload strings and test structure for Aegis Gateway detectors and API contracts.

---
