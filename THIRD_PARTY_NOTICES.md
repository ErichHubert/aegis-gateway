# Third-Party Notices

This project ("Aegis Gateway") uses third-party open source components.
The notices below are provided for attribution and license compliance.

> Note: This file lists **major direct dependencies**. Transitive dependencies are
> documented via `services/inspection/requirements.txt` (Python) and the gateway
> `.csproj`/NuGet references (.NET).

---

## .NET / Gateway

- YARP Reverse Proxy — MIT License  
  Copyright (c) Microsoft Corporation  
  Source: https://github.com/microsoft/reverse-proxy

- ASP.NET Core / .NET — MIT License  
  Copyright (c) .NET Foundation and Contributors  
  Source: https://github.com/dotnet/aspnetcore

---

## Python / Inspection Service

- FastAPI — MIT License  
  Copyright (c) Sebastián Ramírez  
  Source: https://github.com/fastapi/fastapi

- Uvicorn — BSD 3-Clause License  
  Source: https://github.com/encode/uvicorn

- Pydantic — MIT License  
  Source: https://github.com/pydantic/pydantic

- Microsoft Presidio Analyzer — MIT License  
  Copyright (c) Microsoft Corporation  
  Source: https://github.com/microsoft/presidio

- spaCy — MIT License  
  Copyright (c) ExplosionAI GmbH  
  Source: https://github.com/explosion/spaCy

- spaCy model: en_core_web_lg — MIT License  
  Copyright (c) ExplosionAI GmbH  
  Source: https://github.com/explosion/spacy-models

- detect-secrets — Apache License 2.0  
  Copyright (c) Yelp and contributors  
  Source: https://github.com/Yelp/detect-secrets

---

## Code Attribution

Portions of the test data / test cases in this repository were adapted from the
`detect-secrets` project (Apache License 2.0). See the relevant test files for
per-file attribution comments and references.

---

## License Notes

Each third-party component remains licensed under its original license terms.
This notice file does not modify or replace any upstream license.