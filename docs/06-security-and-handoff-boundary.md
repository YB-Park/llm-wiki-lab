# Security and Restricted-Network Handoff Boundary

## Status

Operational guardrail for experiments. This is **not** a statement about the organization's actual data-classification policy; organizational policy always takes precedence.

## Purpose

The project is executed partly in a managed corporate environment where external services may be restricted. Experimental convenience must not create an accidental data-exfiltration workflow.

The LLM Wiki research goal does not justify transferring corporate information to an external system.

## Core rule

> Nothing leaves the managed environment merely because the project believes it is sanitized.

External transfer is allowed only when the organization's applicable policy permits it.

If policy prohibits transfer, even aggregate/synthetic handoff output remains local.

## Default local-only artifacts

Treat the following as local-only unless policy explicitly permits otherwise:

- raw source/work documents;
- wiki states derived from corporate work;
- model prompts and responses;
- OTel/raw telemetry;
- usernames, hostnames, local filesystem paths;
- environment screenshots;
- repository/workspace metadata that may reveal internal structure;
- free-form failure traces containing context;
- tokens/credentials/configuration;
- IDE/editor state.

## Safe-handoff design target

Experiment harnesses should make a policy-compliant transfer possible **without requiring screen captures or copying free-form transcripts**.

A safe-handoff mode should, by design:

- operate only on fictional/public-safe experiment cases;
- emit synthetic case/query IDs rather than source text;
- emit aggregate counts and normalized numeric metrics;
- omit model free-form responses;
- omit absolute/relative local paths;
- omit usernames/hostnames;
- omit raw telemetry payloads;
- omit repository/workspace names when unnecessary;
- avoid stack traces in the normal successful handoff;
- support writing the handoff to a small standalone text file for local inspection.

This design reduces accidental exposure; it does not override organizational policy.

## Failure handling

When an experiment fails inside the restricted environment:

1. keep raw artifacts local;
2. classify whether the failure is harness/infrastructure, model-contract, or experiment-semantic;
3. prefer a local sanitizer that emits only an error code/category and synthetic run ID;
4. do not send a terminal screenshot by default;
5. if debugging requires more detail, first verify what information is permitted to leave the environment.

## Research implication

Security is not only deployment plumbing. A mature personal/corporate knowledge system may need explicit trust zones:

```text
private evidence / work context
        ↓
local semantic processing
        ↓
canonical knowledge + audit log
        ↓
policy-controlled export boundary
```

A model/tool's usefulness does not grant it permission to cross that boundary.

## Relationship to automation research

The same principle that separates **semantic proposal** from **canonical mutation authority** should also separate **local observability** from **external export authority**.

Automation should not silently broaden either authority.

## Current experiment requirement

E009A and later restricted-network experiments should provide a compact safe-handoff mode before scored runs begin.

No experiment is blocked from being run locally merely because external transfer is unavailable; analysis tooling should be capable of producing local reports that a user can inspect without exporting raw artifacts.
