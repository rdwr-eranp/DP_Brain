# DP Brain Maintainer

Workspace for the **DP Brain Maintainer** agent. The agent maintains [`raop-dp-qa-brain`](raop-dp-qa-brain/README.md), the source-grounded DefensePro QA knowledge corpus. RAOP uses the corpus to generate executable test plans from DefensePro User Guides, Release Notes, CLI/OID references, tech specs, capacity data, learning material, and owner/QA evidence.

## Use the agent

In VS Code Copilot Chat, pick **DP Brain Maintainer** in the agent picker and describe the task, for example *"sync and health-check the brain"* or *"add the 10.16 release notes"*.

## Workspace map

| Path | Contents |
|---|---|
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | Always-on rules for this workspace |
| [.github/agents/dp-brain-maintainer.agent.md](.github/agents/dp-brain-maintainer.agent.md) | Agent definition: role, tools, constraints, workflow, output format |
| [.github/instructions/](.github/instructions) | Auto-applied rules for corpus Markdown and brain scripts |
| [docs/brain/overview.md](docs/brain/overview.md) | What the brain is, why, sources, principles, consumers, history |
| [docs/brain/structure.md](docs/brain/structure.md) | Repo layout, branches → KB collections, header/ID scheme, hub docs |
| [docs/brain/pipeline.md](docs/brain/pipeline.md) | Scripts, build on Windows, definition of done |
| [docs/brain/knowledge-bases.md](docs/brain/knowledge-bases.md) | The 10 DP KBs and the `dp-kb-cognito` MCP tools |
| [docs/brain/status.md](docs/brain/status.md) | Health snapshot, known drift, owner-only gaps |
| [docs/agent/operating-model.md](docs/agent/operating-model.md) | Permission matrix and git workflow |
| [docs/agent/roadmap.md](docs/agent/roadmap.md) | Planned skills and flows |
| `raop-dp-qa-brain/` | Brain repo clone (own git, ignored by this workspace) |

## Setup

```powershell
git clone https://eranp-radware@bitbucket.org/rdwr/raop-dp-qa-brain.git
cd raop-dp-qa-brain; python scripts/validate_corpus.py
```

Requirements: Python 3.x and git. Optional: `boto3` plus AWS profile `raop-new-account` for `reconcile_s3.py`, and the `dp-kb-cognito` MCP server for KB grounding. To build on Windows, enable long paths or use the short-path copy described in [pipeline.md](docs/brain/pipeline.md#building-on-windows).
