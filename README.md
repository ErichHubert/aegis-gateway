# Aegis Gateway

**Aegis Gateway** is a security-focused reverse proxy that inspects, evaluates, and controls LLM (or generic HTTP/API) requests *before* they reach a target system.

It is a **reference implementation for LLM / API egress hardening**, with a strong focus on:

- Preventing **PII leaks** and **secret exposure**
- Mitigating **prompt injection** and unsafe request patterns
- Enforcing **policy-based decisions** (`allow` / `confirm` / `block`)
- Staying **operationally realistic**: Docker → Compose → K3s / Service Mesh

---

## Problem & Motivation

Modern applications increasingly call external LLMs or other 3rd-party APIs.  
Typical risks:

- Users (or upstream systems) send **sensitive data** (PII, secrets, tokens)
- **Prompt injection** attempts try to bypass internal guardrails
- There is no **central place** to enforce inspection / policies
- Logs accidentally store **sensitive payloads**

**Aegis Gateway** addresses this by adding a **security inspection layer in front of your target**, without forcing you to re-architect your application.

---

## High-Level Architecture

```text
Client
  ↓
Aegis Gateway (ASP.NET + YARP)
  ├─ Policy Evaluation (Allow / Confirm / Block)
  ├─ Confirm Flow (TTL-based tokens)
  ├─ Logging & Audit Hooks
  ↓
Inspection Service (FastAPI)
  ├─ PII Detection (Presidio + spaCy)
  ├─ Secret Detection (detect-secrets)
  ├─ Prompt Injection Heuristics
  ↓
Target Service
  ├─ Echo (Demo)
  └─ Ollama / LLM (optional)
```

Key properties:

- **Only the gateway** is publicly reachable
- **Inspection Service** is internal, stateless and configuration-driven
- **Policies live in the gateway** (not in the inspector) for clear separation of concerns
- Supports **multiple routes and targets** behind a single gateway

---

## Core Features

- **Reverse Proxy Gateway (ASP.NET + YARP)**
  - Route-based configuration for:
    - Prompt inspection on/off
    - Prompt / payload format
    - Policy ID and severity thresholds
  - Policy engine that maps **severity → action**
  - Type overrides (e.g. `pii_iban` → `block`, even if severity would allow)

- **Inspection Service (FastAPI + Python)**
  - PII detection using **Presidio** + **spaCy**
  - Secret detection via **detect-secrets**
  - Configuration via **YAML** (analyzers, thresholds, categories)
  - Stateless & side-effect-free request processing

- **Confirm Flow**
  - Requests that are not “clean” but not critical can be tagged as `confirm`
  - User / operator can explicitly confirm once
  - Confirm-tokens are server-side validated and time-bound

- **Security & Robustness**
  - Non-root Docker images
  - Read-only file systems with `tmpfs` for temp data
  - Health endpoints for gateway, inspector and (optional) LLM
  - No runtime model downloads
  - No secrets in logs or responses (only references / IDs)

---

## Request Lifecycle

1. **Client** sends a request to the gateway (e.g. `/llm/chat`).
2. **Gateway**:
   - Checks route configuration (inspection enabled? which policy?).
   - Forwards relevant request data to the **Inspection Service**.
3. **Inspection Service**:
   - Runs PII, secret, and heuristic checks.
   - Returns a structured report with findings + computed severity.
4. **Gateway Policy Engine** decides:
   - `allow` → forward request to target
   - `confirm` → return a `ProblemDetails` response requiring confirmation
   - `block` → return a blocking `ProblemDetails` with high-level reason
5. On `confirm`, the client can send a follow-up request with a **confirm token**.

All responses in the control flow use **structured error formats** (ASP.NET `ProblemDetails`) so clients can react programmatically.

---

## Components

### 1. Gateway (ASP.NET + YARP)

- Reverse proxy routing configuration
- Route metadata controls:
  - `InspectionEnabled`
  - `PromptFormat` / payload extraction hints
  - `PolicyId`
- Policy engine:
  - Severity thresholds per policy (e.g. `pii: warn`, `secrets: block`)
  - Type-based overrides
  - Centralized mapping to `allow` / `confirm` / `block`
- Confirm-flow:
  - Short-lived confirm tokens
  - Server-side validation (not trust-on-first-use)

### 2. Inspection Service (FastAPI)

- Single `/inspect` endpoint (JSON in, JSON out)
- Uses:
  - **Presidio** + **spaCy** for PII extraction
  - **detect-secrets** for credential patterns
- Configuration:
  - YAML-based, immutable at runtime
  - Defines analyzers, categories, and mapping to severities

> Design choice: **one inspector = one configuration**.  
> Multi-tenant setups are intentionally out of scope for now.

### 3. Demo Targets

- **Echo Service**
  - Minimal HTTP service that returns back what it receives
  - Used to demonstrate inspection without requiring a real LLM

- **Ollama / LLM (optional)**
  - Optional container for local LLM testing
  - Gateway only talks to Ollama over the internal network

---

## Getting Started

### Prerequisites

- `git`
- `docker` + `docker compose`
- `make` (recommended for DX, optional if you prefer raw `docker compose`)

### 1. Clone the Repository

```bash
git clone https://github.com/<your-org>/aegis-gateway.git
cd aegis-gateway
```

### 2. Run the Echo Demo

```bash
make compose-up-echo
# or:
# docker compose -f docker-compose.echo.yml up --build
```

This starts:

- Aegis Gateway
- Inspection Service
- Echo target service

### 3. Send a Test Request

```bash
curl -X POST http://localhost:8080/echo   -H "Content-Type: application/json"   -d '{"message": "Hello from Aegis Gateway"}'
```

You should see the echo response forwarded through the gateway.

### 4. Trigger Inspection

Send a request that contains obvious PII or secrets:

```bash
curl -X POST http://localhost:8080/echo   -H "Content-Type: application/json"   -d '{"message": "My email is john.doe@example.com and my API key is sk_test_123"}'
```

Depending on the configured policy, you should receive:

- A **blocked** response, or
- A **confirm** response with structured `ProblemDetails`.

Exact behavior is defined in the gateway’s policy configuration.

---

## Configuration Overview

### Gateway Configuration (Routes & Policies)

- Each route defines:
  - Target cluster (e.g. `echo`, `ollama`)
  - Whether inspection is enabled
  - Which policy to apply
- Policies define:
  - Mapping from finding categories to severities
  - Severity thresholds for `allow` / `confirm` / `block`
  - Type overrides (e.g. `pii_iban` or `secret_generic`)

Example (pseudo):

```jsonc
{
  "Routes": [
    {
      "RouteId": "echo-secured",
      "ClusterId": "echo",
      "Inspection": {
        "Enabled": true,
        "PolicyId": "default"
      }
    }
  ],
  "Policies": {
    "default": {
      "SeverityThresholds": {
        "allow": 1,
        "confirm": 2,
        "block": 3
      },
      "Overrides": {
        "pii_iban": "block",
        "secret_generic": "block"
      }
    }
  }
}
```

> See the configuration files in the repo for the exact schema and examples.

### Inspection Service Configuration (YAML)

- Defines which analyzers are enabled
- Configures thresholding and mapping to categories
- Controls PII / secret detection behavior

Example (pseudo):

```yaml
pii:
  enabled: true
  entities:
    - PERSON
    - EMAIL_ADDRESS
    - IBAN
secrets:
  enabled: true
  detectors:
    - high_entropy_strings
    - aws_keys
    - generic_api_keys
```

---

## Security Considerations

Aegis Gateway intentionally includes several hardening measures:

- Non-root containers
- Read-only filesystems (with minimal temp dirs)
- No dynamic downloads at runtime
- Health endpoints for all major components
- No logging of raw secrets or full prompts (configurable, but discouraged)

See [`SECURITY.md`](./SECURITY.md) for:

- Scope of this project
- Reporting security issues (responsible disclosure)
- What is **in scope** vs. **out of scope** for this reference implementation

---

## Deliberate Limitations

To keep the project focused and understandable:

- ❌ No built-in **authentication/authorization**
  - Use existing solutions (OIDC, mTLS, API gateways, service mesh) in front of or around Aegis Gateway.
- ❌ No multi-tenant configuration model in the inspector
  - A single inspector instance has a single configuration.
- ❌ Not a full “product”
  - This is a **security-focused reference architecture**, not a turnkey SaaS.

---

## Testing

The repo contains tests for:

- **Gateway** (.NET)
- **Inspection Service** (Python)

Typical pattern:

```bash
# Gateway tests
dotnet test ./src/Aegis.Gateway.Tests

# Inspection service tests
cd src/inspection-service
pytest
```

Unit and integration tests avoid:

- Real secrets
- Real user data

---

## Development Workflow

Recommended local workflow:

1. Run the full stack with Docker Compose (echo or Ollama).
2. Develop gateway (C#) and inspector (Python) in watch-mode against the running stack.
3. Use the `Makefile` commands as the main DX entry points:
   - `make compose-up-echo`
   - `make compose-up-ollama`
   - `make ollama-pull`

---

## Contributing

Contributions are welcome — especially around:

- New detectors (custom PII / secret patterns)
- Additional policies and real-world examples
- Deployment manifests (K3s, Helm charts)
- CI hardening (SAST, SCA, container scanning)

Please read:

- [`CONTRIBUTING.md`](./CONTRIBUTING.md)
- [`SECURITY.md`](./SECURITY.md)

before opening issues or pull requests.

---

## License

Aegis Gateway is licensed under the **Apache License, Version 2.0**.

See [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE) for details.
