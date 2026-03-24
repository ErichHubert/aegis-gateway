# Third-Party Notices

This project, **Aegis Gateway**, includes and depends on third-party open-source software components.
The original license terms of those components continue to apply.

This document is informational and non-exhaustive. It does not replace upstream license texts, notices, or attribution requirements.

---

## Core Components Referenced by This Repo

### Gateway Service (.NET)
- **YARP (Yet Another Reverse Proxy)** `2.3.0`
  - License: MIT License
- **ASP.NET Core / .NET Runtime & SDK** `10.0`
  - License: MIT License
  - Note: Microsoft container images and distributions may include additional components and notices provided by Microsoft.

### Inspection Service (Python)
- **FastAPI** `0.135.1`
  - License: MIT License
- **Uvicorn** `0.42.0`
  - License: BSD-3-Clause License
- **Pydantic** `2.12.5`
  - License: MIT License
- **pydantic-settings** `2.13.1`
  - License: MIT License
- **Microsoft Presidio Analyzer** `2.2.362`
  - License: MIT License
- **spaCy** `3.8.11`
  - License: MIT License
- **spaCy model `en_core_web_lg`** `3.8.0`
  - License: MIT License
- **detect-secrets** `1.5.0`
  - License: Apache License 2.0

The inspection service also installs additional transitive dependencies from `requirements.txt`; those packages carry their own license terms.

---

## Docker Base Images Used by the Current Dockerfiles

At the time of writing, the repository Dockerfiles reference:

- `mcr.microsoft.com/dotnet/aspnet:10.0-noble-chiseled`
- `mcr.microsoft.com/dotnet/sdk:10.0-noble`
- `python:3.13.12-slim-trixie`

These images may contain additional software components and license notices provided by their respective publishers.

---

## Portions Derived From Other Projects

### detect-secrets (test payload inspiration)
Some test payloads and/or test-case patterns used for validating secret detection behavior were adapted from the `detect-secrets` project and modified to fit this repository’s test suite and contracts.

- Upstream project: `detect-secrets`
- License: Apache-2.0
- Modifications: Adapted payload strings and test structure for Aegis Gateway detectors and API contracts.
