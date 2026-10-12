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
| [docs/brain/pipeline.md](docs/brain/pipeline.md) | Scripts, build on Windows, AWS deploy flow, definition of done |
| [docs/brain/knowledge-bases.md](docs/brain/knowledge-bases.md) | The 10 DP KBs and the `dp-kb-cognito` MCP tools |
| [docs/brain/status.md](docs/brain/status.md) | Health snapshot, known drift, owner-only gaps |
| [docs/agent/operating-model.md](docs/agent/operating-model.md) | Permission matrix and git workflow |
| [docs/agent/roadmap.md](docs/agent/roadmap.md) | Planned skills and flows |
| [scripts/deploy_brain.py](scripts/deploy_brain.py) | Byte-diff deploy of `build/` to the S3 buckets plus Bedrock ingestion (`--apply` needs approval) |
| [CHANGELOG.md](CHANGELOG.md) | Brain PRs, KB deploys (ingestion job IDs), and workspace changes |
| `raop-dp-qa-brain/` | Brain repo clone (own git, ignored by this workspace) |

## Setup

Clone this workspace, then clone the brain inside it. The brain is git-ignored here and keeps its own history.

```powershell
git clone https://github.com/rdwr-eranp/DP_Brain.git; cd DP_Brain
git clone https://bitbucket.org/rdwr/raop-dp-qa-brain.git
cd raop-dp-qa-brain; python scripts/validate_corpus.py   # expect Errors: 0
```

Requirements:

- Python 3.x and git. The brain scripts are standard-library only.
- For AWS work: `boto3` (`pip install boto3`), AWS CLI v2, and an SSO profile for account `002889194435` in `eu-central-1`. Log in with `aws sso login --profile <your-profile>`. `deploy_brain.py` defaults to `FullAdminAccessBesidesUserMGMT-002889194435`; if your profile has another name, pass `--profile <name>`.
- The `dp-kb-cognito` MCP server, for KB grounding and post-deploy smoke tests.
- To build on Windows: enable long paths, or build from a short-path worktree as described in [pipeline.md](docs/brain/pipeline.md#building-on-windows).

## Working together

- **Brain changes:** use a `brain/<topic>` branch, then open a Bitbucket PR, review, and merge. Never commit directly to `main`.
- **Deploys:** follow the procedure in [pipeline.md](docs/brain/pipeline.md#deploy-explicit-user-approval-required) for every deploy. Plan first, `--apply` only after approval, then re-plan to 0 changes and smoke-test.
  - Tell the other maintainer before each `--apply`, so two deploys don't run at once.
  - Record the deploy, with its ingestion job IDs, in [CHANGELOG.md](CHANGELOG.md).
- **Health:** [status.md](docs/brain/status.md) is the current snapshot. Its "Still open" list needs the owner's decisions.

## Memory-candidate harvest (read-only)

The long-term-memory governance table (`raop-prod-memory-governance`, account `002889194435`) can be read to harvest candidate facts from user interactions. Use [scripts/harvest_memory_candidates.py](scripts/harvest_memory_candidates.py) to page the full review queue, group candidates by feature, and generate a review report against the brain.

- **Read-only only:** list and analyze candidates from DynamoDB; never approve or reject by writing the table directly.
- **Decisions:** if Guy wants to close or approve candidates, do it through the REST API from his guide, not DynamoDB writes.
- **Current pilot:** `bdos-signature-sync`, with raw exports kept outside git and reports written under `out/` (git-ignored).
