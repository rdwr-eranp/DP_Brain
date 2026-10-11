# DefensePro knowledge bases and the dp-kb-cognito MCP

The brain is one of 10 DefensePro KBs behind the RAOP runtime (Bedrock, `eu-central-1`). The maintainer agent queries them through the **`dp-kb-cognito`** MCP server to ground every new fact. Physical KB IDs are environment-owned. Use only the logical names.

## The 10 sources

| MCP source | Logical KB | Authority | Use it for |
|---|---|---|---|
| `dp_user_guide` | `dp_user_guide_kb` | authoritative | Navigation path, screen, profile procedure, parameter name, range, default, monitoring screen |
| `dp_cli_oid` | `dp_cli_oid_kb` | authoritative | CLI syntax, command tree position, switches, SNMP OIDs |
| `dp_release_notes` | `dp_release_notes_kb` | authoritative | Version-specific behavior, new features, fixes, known issues, supported platforms |
| `dp_capacity` | `dp_capacity_kb` | authoritative | Max values, per-platform/per-table limits (current source is v10.10, version-mismatched) |
| `dp_tech_specs` | `dp_tech_specs_kb` | authoritative | Models, throughput tier, ports, licensing form |
| `dp_learning` | `dp_learning_kb` | authoritative (treated as secondary by the brain) | Detection/mitigation concepts, module deep dives |
| `dp_qa_brain_product` | `dp_qa_brain_product_kb` | curated_synthesis | **This brain**: product-synthesis collection |
| `dp_qa_brain_guidance` | `dp_qa_brain_guidance_kb` | curated_guidance | **This brain**: qa-guidance collection |
| `dp_auto_infra` | `dp_auto_infra_kb` | authoritative | Automation framework/infrastructure code |
| `dp_auto_tests` | `dp_auto_tests_kb` | authoritative | Automation test code and suites |

Default search set: `dp_qa_brain_product`, `dp_user_guide`, `dp_cli_oid`, `dp_release_notes`, `dp_auto_infra`, `dp_auto_tests`.

## MCP tools for maintenance

| Tool | Use in maintenance |
|---|---|
| `resolve_version` | Validate a version string against the live release catalog before you write it into a header |
| `search` (source, software_version, top_k) | Raw passages + metadata. **Primary tool for grounding and citation.** |
| `ask` (source) | Quick cited answer from one source |
| `list_skills` / `run_skill` | Runtime QA workflows (for example, `version_aware_configuration`, `cli_command_assistant`, `protection_module_troubleshooting`). Use these to smoke-test what the brain produces. |
| `agent_answer` | Open-ended question (end-to-end runtime behaviour) |
| `evaluation_health_check` | Deployed source and positive-control health gate. Run it after an ingestion. |

## Grounding rules

- Always pass family and exact release (`software_version`) when querying authoritative KBs. Reject results from the other family.
- Map each fact to a catalogued `source://` ID (for example, `DP-UG-10.15.0.0`). If no ID fits, add one to the source catalog first.
- Querying `dp_qa_brain_*` returns the **deployed** brain, which may lag the repo. Use it to detect drift or to smoke-test after ingestion, never as evidence for itself.
- Retrieval contract (see [kb-integration.md](../../raop-dp-qa-brain/docs/kb-integration.md)): exact-version filters exclude `cross-family` chunks, so the runtime needs a union of exact-version and cross-family results. Keep cross-family docs free of a single `Software version`.
