# Security Policy

This project (**Aegis Gateway**) is a security-focused reverse proxy and inspection service. Security issues are taken seriously.

## Reporting a Vulnerability

**Please do not open public GitHub issues for security vulnerabilities.**

Preferred reporting channel:
- Use GitHub’s **“Report a vulnerability”** (Security Advisories) for this repository, if enabled. This keeps the report private.

If Security Advisories are not available:
- Open a minimal GitHub issue **without exploit details**, and request a private channel for disclosure.

## What to Include in a Report

To help reproduce and fix the issue quickly, include:
- A clear description of the vulnerability and impact
- Steps to reproduce (preferably with minimal PoC)
- Affected component(s) (gateway, inspection service, docker/compose, policies, confirm flow)
- Version / commit SHA and environment details (OS, Docker, .NET/Python versions)
- Any logs or stack traces **with secrets removed**
- A suggested fix/mitigation (optional)

## What NOT to Include

- Real secrets, API keys, tokens, production credentials
- Real user prompts, customer data, or any private data
- Full exploit chains posted publicly

Use synthetic examples (e.g., `FAKE_TOKEN_...`) when demonstrating detections.

## Scope

In scope:
- Vulnerabilities in the gateway (policy enforcement, confirm flow, routing)
- Vulnerabilities in the inspection service (PII/secret detection pipeline, config handling)
- Request/response handling issues which could lead to leakage, bypass, SSRF, header injection, etc.
- Security-relevant misconfigurations shipped as defaults in this repo

Out of scope (typically):
- Issues in third-party dependencies (report upstream as well)
- Denial-of-service via untrusted infrastructure or intentionally massive inputs (unless there’s an obvious fix)
- “Missing best practices” without a concrete security impact

## Coordinated Disclosure

If you report a valid vulnerability, the maintainer will:
- Acknowledge receipt
- Work with you on a fix
- Coordinate disclosure timing if public disclosure is planned

This is a personal/open-source project; response times are best-effort, but security issues are prioritized.

## Supported Versions

Security fixes are typically applied to the **latest** version on the default branch. If a release/tag exists, it will be noted in the advisory or release notes.

## Security Notes (Project Intent)

This repository includes demo and local development configurations. Even with security-minded defaults, it is **not** a drop-in production deployment.

For production hardening you would typically add:
- Strong authentication/authorization at the edge (OIDC, mTLS, or both)
- Rate limiting and abuse protection
- Strict outbound egress controls (avoid SSRF)
- Centralized audit logging and alerting
- Secret management and key persistence (e.g., ASP.NET DataProtection keys)
- Network policies/service mesh mTLS in Kubernetes

## Thank You

Thanks for helping improve Aegis Gateway’s security.
