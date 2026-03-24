# Data Handling

This file describes the technical data-handling posture of the shipped **Aegis Gateway** repository. It is **not** a privacy notice, controller/processor agreement, or legal advice.

## What the Repo Processes

The reference implementation may process:

- Prompt or payload content extracted for inspection
- Optional metadata forwarded by the gateway, such as `userId` and `source`
- Derived inspection findings, including finding types, severities, and detector-local detail inside the internal service boundary
- Operational metadata such as trace IDs, route IDs, status codes, and health-check events

## Default Flow in This Repo

1. The gateway reads the request body to extract the prompt or relevant payload segment.
2. The gateway forwards the extracted prompt and optional metadata to the internal inspection service.
3. The inspection service returns findings to the gateway for policy evaluation.
4. The gateway returns `allow`, `confirm`, or `block` behavior based on policy.

The current reference implementation returns structured control responses. Depending on route behavior and policy decisions, those responses may include finding detail that an operator may wish to minimize or redact before using the project with real data.

## Logging and Response Behavior

- The gateway logs route, policy, and finding-count information for inspection decisions.
- The inspection service logs prompt length, source, optional user ID, and finding counts/types.
- Unhandled exceptions are logged server-side with full exception details for debugging.
- Review the gateway’s error responses in your own environment and ensure they only expose the level of detail you are willing to return to clients.

Operators should treat logs and exception sinks as potentially sensitive. This repo does not configure external log storage, SIEM pipelines, or retention rules for you.

## Retention and Deletion

This repository does **not** implement:

- A built-in retention schedule for prompts, findings, or logs
- Automatic deletion workflows or data-subject request handling
- Region-specific legal analysis, transfer controls, or record-keeping obligations

The operator of a deployment is responsible for deciding what is stored, for how long, where it is stored, and who can access it.

## Operator Responsibilities

Before using this project with real data, review and configure at least:

- Lawful basis, notices, and internal privacy/compliance approvals
- Access controls for gateways, logs, metrics, and tracing systems
- Data minimization for request forwarding and logging
- Encryption, backup, retention, and deletion policies
- Incident response and audit requirements

## Known Limits

- Detection can produce false positives and false negatives.
- Confirm tokens are currently stored in process-local memory inside the gateway.
- Multi-instance deployments currently require a single gateway replica or request affinity for the confirm flow.
- Production deployments still need external authentication, authorization, rate limiting, and egress controls.
