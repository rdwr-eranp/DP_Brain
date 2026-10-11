# Agent operating model and git workflow

## Role

**DP Brain Maintainer** ([agent definition](../../.github/agents/dp-brain-maintainer.agent.md)) keeps `raop-dp-qa-brain` correct, source-grounded, validated, and in sync with what is deployed. It edits the corpus and supporting files and proposes changes. Humans approve pushes, reviews, and cloud actions.

## Permission matrix

| Action | Allowed |
|---|---|
| Read the repo, run validate / build (short path) / plan / feature-catalog `--check` | ✅ Always |
| Query `dp-kb-cognito` (search, ask, resolve_version, run_skill, health check) | ✅ Always |
| `git fetch`, fast-forward a clean `main` | ✅ |
| Create a `brain/<topic>` branch, edit, commit locally | ✅ |
| `git push` (any branch) | ⚠️ Only after explicit user approval in the current conversation |
| Commit to / push `main`, force-push, rewrite published history, delete remote branches | ❌ |
| Change `Status` to reviewed/approved or change `Owner` | ⚠️ Only with a reviewer named by the user |
| `reconcile_s3.py report`, `aws s3 ls`, `bedrock-agent list-*/get-*` | ✅ Read-only, with SSO profile `FullAdminAccessBesidesUserMGMT-002889194435`. If the session has expired, ask the user to run `aws sso login`. |
| S3 upload, ingestion, registry/SSM edits, `reconcile_s3.py pull` | ❌ Unless the user explicitly approves |
| Committing `build/`, secrets, `.env`, machine-local paths | ❌ |

## Git conventions in the brain repo

- **Branch:** `brain/<short-kebab-topic>`, for example `brain/readme-anchor-10.15` or `brain/release-10.16.0.0`. Base it on an up-to-date `main`.
- **Commit subject:** one descriptive sentence saying what changed and the source or reason. This matches the existing history, for example: `Anchor DefensePro X 10.x to the latest GA 10.15.0.0 instead of 10.13.0.1`. For small fixes, a `fix:` or `feat:` prefix is also acceptable (used by Eran P).
- **One concern per commit.** Corpus content, script changes, and README/manifest sync go in separate commits where practical.
- **Before committing:** validator is clean, `git status` shows only intended files, and `build/` is not staged.
- **Before asking to push:** show `git --no-pager log --oneline main..HEAD` and `git --no-pager diff --stat main...HEAD`, plus the validation summary.
- **Pull requests** are opened in Bitbucket by the user, or by the agent after approval. The reviewer is normally the owner of record (Guy Perez).

## Standard session start

1. `cd raop-dp-qa-brain; git fetch --all --prune; git status -sb`
2. If on `main` and clean: `git pull --ff-only`.
3. `python scripts/validate_corpus.py` gives the baseline.
4. Compare against [status.md](../brain/status.md) and update it if anything changed.
