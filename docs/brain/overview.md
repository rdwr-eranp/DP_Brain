# DefensePro QA Brain overview

> Summary for the maintainer agent. The authoritative descriptions are the brain [README](../../raop-dp-qa-brain/README.md) and [docs/](../../raop-dp-qa-brain/docs). Snapshot taken 2026-10-11 at commit `78261d6`.

## What the brain is

`raop-dp-qa-brain` is an **agent-oriented, source-grounded knowledge corpus** for Radware **DefensePro**. RAOP (the QA test-plan generation runtime) uses it to write exact, executable QA test plans instead of generic "configure and send traffic" steps.

- **Repo:** `https://bitbucket.org/rdwr/raop-dp-qa-brain.git` (Bitbucket workspace `rdwr`)
- **Default branch:** `main`. One other branch is `brain/releases-10.14-10.15-and-10.16-planned`, already merged (identical to `main`).
- **Owner of record:** Guy Perez (DefensePro QA). Every corpus doc is `Status: reviewed`, `Last reviewed: 2026-10-08`.
- **Contributors:** Guy Perez (most commits), Eran P (release chronology, feature catalog, BDoS CLI).

## Why it exists

A model that knows only a feature name writes incomplete steps. An executable plan needs parameter names, object dependencies, policy binding, activation proof, exact traffic fields/rates/timeline, module-specific events, receiver evidence, recovery, and source/version lineage.

The brain supplies those **relationships**. It also **routes** the agent to the authoritative product knowledge bases for exact values. It never replaces those KBs. Unsupported facts stay `TBD` with a named owner.

## What it gathers from

The brain is a curated synthesis over these sources. Each one has a stable ID in [source-catalog.md](../../raop-dp-qa-brain/sources/source-catalog.md):

| Source kind | Examples (source IDs) | Governs |
|---|---|---|
| User Guides | `DP-UG-8.35.5.0`, `DP-UG-10.13.0.1`, `DP-UG-10.14.0.0`, `DP-UG-10.15.0.0`, UG collections 8x/10x | Procedures, parameters, documented behavior |
| Release Notes | `DP-RN-8.35.5.0`, `DP-RN-10.0.0.0` … `DP-RN-10.15.0.0`, RN collections 8x/10x | Exact build/platform support, upgrades, release changes |
| CLI / OID references | `DP-CLI-8.35.5.0`, `DP-CLI-10.13.0.1`/`10.14`/`10.15`, `DP-OID-*` | Exact command syntax and identifiers |
| Tech specs / capacity | `DP-TECH-X-2025-08-13`, `DP-CAP-X-10.10-2025-07` (version-mismatched) | Models, ports, limits |
| Learning | `DP-LEARNING-LOCAL-MULTIVERSION` | Secondary conceptual material only |
| Owner/implementation evidence | `DP-IMPL-8X/10X-EVENT-PRIORITIES`, `DP-OWN-1014/1015/1016-*`, `DP-OWN-BACKLOG-COMMITTED`, `DP-OWNER-DOCS` | Narrow, exact questions only (for example, enum order or planned 10.16 features) |
| QA/lab evidence | `DP-QA-LAB-CATALOG-V2`, `RAOP-TRAFFIC-TOOL-REGISTRY`, BDoS sync review/xray/evidence | Lab method, tool capability |
| Cyber Controller | `CC-REQ-CLOUD-WDDOS-THROUGHPUT`, `CC-BRAIN-CODE-INDEX` | CC-side behavior and code evidence |

Installation guides and release-matched 10.13+ capacity data are **not** in the corpus yet (see [status](status.md)).

## Core principles the agent must preserve

1. **Family before feature.** DefensePro 8.x and DefensePro X 10.x are separate software streams. The resolution chain is:
   `software family -> exact release/build -> exact release-note-supported platform -> manager version -> form/mode -> capture path -> license -> feature/procedure`.
2. **Anchors** ([corpus-manifest.json](../../raop-dp-qa-brain/corpus-manifest.json)): 8.x = **8.35.5.0** (build 141). 10.x = **10.15.0.0** (moved from 10.13.0.1 on 2026-10-08 by `reground_release.py`). **10.13.0.1** is retained only for content the newer manuals dropped (for example, Quantile DoS, removed in 10.14.0.0). 10.16 is *planned* (owner draft FRD/SRS, unreleased).
3. **Authority precedence.** Release Notes govern build/platform/upgrade eligibility. User Guides govern procedures and behavior. CLI/OID governs identifiers. Learning material is secondary. The brain itself is *curated QA synthesis/guidance*, never vendor authority.
4. **Activation before assertion.** `global -> prerequisites/classes -> profile/rule -> enabled policy/binding -> Submit -> apply/reset -> verify active -> traffic`.
5. **No invented owner facts.** Addresses, certificates, entitlements, lab assignments, rates, thresholds, durations, and tolerances belong to the environment or requirements, not the brain.
6. **Preserve conflicts.** LACP on X10/X20 (10.13 RN vs UG), public XVA AWS-only vs AWS+Azure, X10/X20 port counts (10.2 RN vs 2025 tech sheet), and `EVENT_PRIORITIES` comment/declaration tensions all stay open until an owner resolves them.

## Who consumes it

```
corpus/ --validate--> build/ (chunks + .metadata.json) --deploy_brain.py --apply (approved)--> S3 --Bedrock ingestion--> 2 KBs
                                                                                                         |
          RAOP runtime (raop-runtime-common kb_routing.py, server.py, dp-kb-cognito MCP) <---------------+
```

- **Bedrock KBs:** `dp_qa_brain_product_kb` (product-synthesis) and `dp_qa_brain_guidance_kb` (qa-guidance), region `eu-central-1`.
- **Runtime routing:** `raop-runtime-common/src/raop_runtime_common/kb_routing.py`. Don't add another router.
- **server.py entity resolution** uses `feature_catalog.json`. The catalog is mirrored into the server dir when the brain is checked out there as `_brain/`.
- **dp-kb-cognito MCP** (available to this agent) queries all 10 DP KBs. See [knowledge-bases.md](knowledge-bases.md).

## Creation history (high level)

| Period | Milestone |
|---|---|
| ≤ 2026-08 | Initial 10.13-centred corpus. 2026-08-20 semantic review (`semantic-review/`) expanded it to separate 8.x / 10.x families with cross-family metadata (verdict at the time: NEEDS_CHANGES on runtime filtering and validation gaps). |
| 2026-10-05 | Release chronology / feature-version map, feature catalog moved into the brain, BDoS signature sync evidence |
| 2026-10-06/07 | DUT setup CLI procedures, deterministic mitigation and engine pinning, PSSLO-dependent features, 10.14/10.14.1/10.10.7/10.15 deltas, cloud features, 10.16 planned |
| 2026-10-08 | Anchor moved to 10.15.0.0. Every doc reviewed and owned by Guy Perez. Sections split to fit 3,000-character planner excerpts. |
| 2026-10-11 | 10.16 SRS updates (PSSLO 60 s aggregation), PSSLO statistics required coverage |
