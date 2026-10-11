# DP Brain Maintainer workspace

This workspace builds and runs an agent that maintains the **DefensePro QA Brain** (`raop-dp-qa-brain`), the curated, source-grounded knowledge corpus that RAOP uses to generate executable DefensePro QA test plans.

## Layout

| Path | What it is |
|---|---|
| `raop-dp-qa-brain/` | Clone of the brain repo (`https://eranp-radware@bitbucket.org/rdwr/raop-dp-qa-brain.git`). It has its own git history; this workspace never commits it. |
| `.github/agents/dp-brain-maintainer.agent.md` | The maintainer agent definition |
| `.github/instructions/` | File-scoped rules (corpus authoring, brain scripts) |
| `docs/brain/` | What the brain is, its structure, pipeline, knowledge bases, and current status |
| `docs/agent/` | Agent operating model, git workflow, skills roadmap |

Start with [docs/brain/overview.md](../docs/brain/overview.md). Read [docs/brain/status.md](../docs/brain/status.md) before reporting the brain's health.

## Non-negotiable rules

- **The brain's own docs win.** [README](../raop-dp-qa-brain/README.md), [authoring guide](../raop-dp-qa-brain/docs/authoring-guide.md), and [KB integration](../raop-dp-qa-brain/docs/kb-integration.md) are authoritative for the brain. Workspace docs summarize and link to them. If they conflict, follow the brain and fix the summary.
- **DefensePro 8.x and DefensePro X 10.x are separate families.** Never carry a fact, table, command, default, or platform from one family to the other. Pre-8 operative content is rejected.
- **Never invent product facts.** Values come from cited authoritative sources (User Guide, CLI/OID, Release Notes, capacity, tech specs) or remain `TBD` with an owner.
- **Validate before proposing.** Run `python scripts/validate_corpus.py` in `raop-dp-qa-brain/` after any brain change; it must report `Errors: 0`.
- **Git:** work on a `brain/<topic>` branch, commit locally, and **push only after explicit user approval**. Never commit to or push `main` directly, never force-push, never commit `build/`.
- **No cloud mutation.** Do not upload to S3, start ingestion, run `scripts/deploy_brain.py --apply`, or run `reconcile_s3.py pull` without explicit approval. Deploy with `deploy_brain.py` (byte-diff plan → approval → `--apply`), not `aws s3 sync`. Plan mode, `reconcile_s3.py report` and `aws ... list/get/ls` calls are read-only; use SSO profile `FullAdminAccessBesidesUserMGMT-002889194435` (see [pipeline](../docs/brain/pipeline.md#aws-deployment)).

## Environment gotchas (Windows)

- Python 3.14 is on PATH as `python`. Brain scripts are stdlib only, except `reconcile_s3.py`, which needs `boto3` (installed). The workspace `scripts/deploy_brain.py` also needs `boto3`.
- `build_corpus.py` fails under this workspace path with `FileNotFoundError` because some output paths exceed 260 characters and `LongPathsEnabled=0`. Build from a short-path copy. See [docs/brain/pipeline.md](../docs/brain/pipeline.md#building-on-windows).
- `reground_release.py` expects normalized manuals at `C:\raop-workspace\.dp_doc`.
