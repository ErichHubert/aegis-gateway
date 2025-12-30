# Contributing

Thanks for your interest in contributing to **Aegis Gateway**.

Aegis Gateway is a security-focused reverse proxy (YARP/.NET)
combined with a prompt inspection service (FastAPI/Python) for detecting **secrets**, **PII**, and **prompt injection**
signals.

Contributions are especially welcome in improving detection (rules, heuristics, false-positive/false-negative tuning), as well as documentation, tests, reliability, and security hardening.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Project Goals & Non-Goals](#project-goals--non-goals)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Repo Structure](#repo-structure)
- [Running Locally](#running-locally)
- [Testing](#testing)
- [Code Style & Quality](#code-style--quality)
- [Security Guidance](#security-guidance)
- [Licensing of Contributions](#licensing-of-contributions)
- [Release & Versioning](#release--versioning)

---

## Code of Conduct

Be respectful and constructive. Harassment and discrimination are not tolerated.
If you cannot follow this, please do not contribute.

---

## Project Goals & Non-Goals

Aegis Gateway aims to provide a secure, configurable gateway layer for LLM/AI backends (and similar HTTP services), including request inspection, policy enforcement, and auditable decisioning.

Primary goals:
- **Security & compliance controls**: detect and handle secrets, PII, and prompt-injection signals.
- **Policy-driven enforcement**: allow/confirm/block flows with transparent, testable rules.
- **Operational readiness**: container-first, health checks, reproducible builds, and sensible defaults.
- **Extensibility**: detectors and policies should be easy to extend without rewriting the system.

Non-goals (for now):
- Being a full IAM product (AuthN/AuthZ can integrate with existing identity providers later).
- Being a full SIEM/log pipeline (we focus on emitting structured logs/events).
- Replacing DLP suites; Aegis is a gateway-centric control plane.

If you’re unsure whether a change fits the scope, open an issue describing your idea and the intended use case.

---

## How to Contribute

### 1) Open an Issue (Recommended)
Before starting larger changes, open an issue describing:
- the problem
- the proposed solution
- any alternatives you considered

### 2) Fork & Branch
- Fork the repo
- Create a feature branch:
  - `feature/<short-description>`
  - `bugfix/<short-description>`
  - `docs/<short-description>`

### 3) Make Small, Reviewable PRs
Prefer PRs that are:
- focused (one topic)
- tested
- well described
- easy to revert

### 4) Create a Pull Request
Your PR description should include:
- what changed and why
- how to test it locally
- any security implications

---

## Development Setup

### Prerequisites
- **Docker** + **Docker Compose**
- **Make**
- **.NET SDK** (matching the gateway)
- **Python 3.11+** (matching the inspection service)

### Optional (helpful)
- `curl` (health checks / manual API calls)
- `jq` (pretty-printing JSON)

### Python environment (Inspection Service)

The inspection service uses a standard virtual environment and pinned dependencies.

**Create and activate a virtual environment**:

```bash
cd services/inspection
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

**Install dependencies** (choose one):

- If you commit compiled/pinned requirements:

  ```bash
  python -m pip install -r requirements.txt
  python -m pip install -r requirements-dev.txt
  ```

- If you use `pip-tools` (`*.in` files) and want to (re)generate pins locally:

  ```bash
  python -m pip install -U pip-tools

  # Compile lockfiles
  pip-compile requirements.in -o requirements.txt
  pip-compile requirements-dev.in -o requirements-dev.txt

  # Install the pinned versions
  python -m pip install -r requirements.txt
  python -m pip install -r requirements-dev.txt
  ```

**Run tests**:

```bash
python -m pytest -q
```

---

## Repo Structure

Typical layout:

- `services/gateway/` — .NET gateway (YARP reverse proxy, policies, confirm flow)
- `services/inspection/` — Python FastAPI inspection service (PII, secrets, prompt injection)
- `docker-compose.yml` — local demo setups (echo / optional Ollama)
- `Makefile` — developer entry points (tests, run, compose, etc.)
- `.github/` — CI workflows

---

## Running Locally

### Recommended: Docker Compose

Aegis supports two demo modes:

- **Echo mode (lightweight, no LLM required)**

  ```bash
  make compose-up-echo
  ```

- **Ollama / LLM mode (heavier, realistic prompts)**

  ```bash
  make ollama-pull
  make compose-up-ollama
  ```

Stop and clean:

```bash
make compose-down
```

> Note: The gateway should be the only public entrypoint (typically port `8080`).
> Other services should only be reachable inside the Docker network unless explicitly exposed.

### Run services without Compose (advanced)
Inspection service (run tests, then run the service):

```bash
make inspection-test
make inspection-run
```

Gateway (run tests, then run the service):

```bash
make gateway-test
make gateway-run
```

---

## Testing

### What we expect in PRs
If your PR changes behavior (policies, detectors, confirm flow), tests should be updated or added.

### Run all tests
```bash
make gateway-test
make inspection-test
```

### Notes on test data
- **Do not** include real secrets or production tokens in tests.
- Avoid strings that trigger GitHub secret scanning if possible.
- Prefer clearly synthetic patterns like `FAKE_...`, `TEST_...`, or modified prefixes.

---

## Code Style & Quality

### General
- Prefer clarity over cleverness.
- Keep changes minimal and well-scoped.
- Add comments only where they remove ambiguity or explain non-obvious security decisions.

### .NET (Gateway)
- Keep policy evaluation deterministic.
- Avoid introducing shared mutable global state.
- Prefer immutable configuration objects (options binding) and pure evaluation logic.
- If you add a new policy action or header behavior, add tests.

### Python (Inspection Service)
- Config should be loaded once at startup and treated as immutable.
- Detectors should be stateless after initialization where possible.
- Be careful with libraries that mutate global state (e.g., `detect-secrets` settings). If you introduce
  settings mutation, document and protect it (lock or process isolation), and add tests.

---

## Security Guidance

### Responsible Disclosure
If you believe you found a security issue:
- Do **not** open a public issue with exploit details.
- Follow the process in `SECURITY.md`
- Do not include real user prompts, secrets, or customer data anywhere.

### Threat Model Expectations (high level)
- The gateway should not expose internal services directly.
- Confirm tokens must be short-lived and bound to request context.
- Findings may include sensitive metadata — avoid returning full secrets or raw prompt content by default.

---

## Licensing of Contributions

This project is licensed under the **Apache License 2.0**.

By submitting a pull request, you agree that your contribution is licensed under the same license (Apache-2.0).

No Contributor License Agreement (CLA) is required.

---

## Release & Versioning

This repo may use tags/releases to mark milestones and track user-facing changes.

If you contribute changes that impact behavior, please:
- note it in the PR description
- consider updating docs (README / docs)
- if a changelog exists, add an entry

---

## Thank You

Thanks again for helping improve Aegis Gateway. This project is built to help teams apply security and compliance controls. Even small improvements (docs, tests, typos, examples) are valuable.
