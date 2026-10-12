# Skills and flows roadmap

Planned skills (`.github/skills/<name>/SKILL.md`) and prompts for the maintainer agent. Build them one at a time. Each skill bundles its scripts and checklists.

| # | Skill / flow | Trigger | Core steps | Status |
|---|---|---|---|---|
| 1 | `brain-sync-and-health` | "sync", "health check", session start | fetch/ff `main` → validate → short-path build → plan dry-run → (optional) S3 report → update `docs/brain/status.md` | Planned |
| 2 | `brain-add-release` | New DP release notes / UG / CLI available | `resolve_version` → source-catalog entries → release-inventory → feature-version-map → family/availability docs → open questions → validate | Planned |
| 3 | `brain-reground-anchor` | Move 10.x anchor (for example, 10.15 → 10.16) | `reground_release.py audit` → review report → `apply` → manifest/README/validator anchors → validate/build | Planned |
| 4 | `brain-author-doc` | Add or update a feature/protection/workflow doc | locate hub docs → retrieve facts per KB → header + sections + Sources → catalog/feature_catalog → validate | Planned |
| 5 | `brain-drift-audit` | "is the README/manifest/S3 in sync" | README vs manifest/validator counts, kb-integration smoke text, S3 report, deployed-KB spot checks via `dp-kb-cognito` | Planned |
| 6 | `brain-gap-triage` | Owner answered a question / new TBD | update open-questions + ownership-handoff, propagate resolution to affected docs | Planned |
| 7 | `brain-prepare-review` | Ready to push | diff/log summary, validation evidence, commit hygiene, ask approval, push, draft PR description | Planned |
| 8 | `brain-deploy-kb` | PR merged to `main`, "deploy", "sync the buckets" | short-path worktree of `origin/main` → validate → build → `scripts/deploy_brain.py` plan → user approval → `--apply` (S3 put/delete + ingestion + poll) → re-plan = 0 → `dp-kb-cognito` smoke test → update `status.md` and `CHANGELOG.md` → remove worktree | Script ready ([pipeline](../brain/pipeline.md#deploy-explicit-user-approval-required)); skill planned |
| 9 | `brain-harvest-memory-candidates` | "review memory candidates", "use long-term memory", "harvest governed memory" | query `raop-prod-memory-governance` read-only → group by feature → compare against brain docs and source catalog → flag unknown IDs / uncited owner answers / drift / reviewer instructions → write report under `out/memory-harvest/` → propose corpus follow-ups and, optionally, REST-API decisions | Pilot script ready: [harvest_memory_candidates.py](../../scripts/harvest_memory_candidates.py) |

Candidate next fix branches (need owner decisions): the "Still open" items in [status.md](../brain/status.md#still-open). The first fix branch (README/kb-integration anchor staleness) shipped as brain PR #1; see the [CHANGELOG](../../CHANGELOG.md).
