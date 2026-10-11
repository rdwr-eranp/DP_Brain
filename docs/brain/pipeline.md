# Brain pipeline and scripts

All commands run from `raop-dp-qa-brain/`. Every script except `reconcile_s3.py` is standard-library only and makes no network calls.

## Lifecycle

```
author corpus/ ──► validate_corpus.py ──► build_corpus.py ──► build/ ──► plan_provisioning.py (dry-run JSON)
                                                                   │
                                     (explicit approval) upload to S3 ─► Bedrock ingestion ─► smoke tests
                                                                   │
                                          reconcile_s3.py report ◄─┘  (drift check: S3 vs build/)
```

## Scripts

| Script | Purpose | Typical command | Side effects |
|---|---|---|---|
| `validate_corpus.py` | Checks manifest schema 3, anchors, collections cover corpus, headers, unique IDs, `source://` IDs catalogued, applicability scope rules, Sources sections, relative links, no local paths, no pre-8 content, FPGA/EZchip boundary, README platform table = canonical doc | `python scripts/validate_corpus.py` | None. Prints counts and `Errors: N. Warnings: N.` |
| `build_corpus.py` | One chunk per H2 (oversized sections split by `###`/paragraph/table rows to fit 3,000 chars). Repeats provenance, writes `.metadata.json` sidecars (≤1,024 bytes), rewrites links to `kbdoc://`, writes `build/build-manifest.json` (schema 2) with SHA-256 | `python scripts/build_corpus.py` | Rewrites `build/` (git-ignored) |
| `plan_provisioning.py` | Deterministic provisioning proposal (`execution_mode=dry-run`, `mutations=[]`) | `python -B scripts/plan_provisioning.py` | Stdout only |
| `build_feature_catalog.py` | Turns `03-protections/catalog.md` + `feature-alias-overrides.json` into `feature_catalog.json` (22 features). Mirrors to server dir when checked out as `_brain/` | `python scripts/build_feature_catalog.py [--check] [--output PATH]` | Writes `feature_catalog.json` |
| `reground_release.py` | Moves 10.x citations from one exact release to another. `audit` checks CLI nodes/switches, CLI line ranges, quoted UG passages, and table captions against the target manuals and writes `build/reground-<from>-to-<to>.md`. `apply` rewrites only what the audit proved. | `python scripts/reground_release.py audit --from 10.15.0.0 --to 10.16.0.0` | Needs manuals at `C:\raop-workspace\.dp_doc`. `apply` edits corpus. |
| `reconcile_s3.py` | `report`: byte-compares S3 objects vs `build/`. `pull`: reconstructs authored docs from S3-only chunks. | `python scripts/reconcile_s3.py report [--strict]` | Needs `boto3` and an AWS profile (hardcoded `raop-new-account`; see [AWS access](#aws-access-from-this-workstation)), region `eu-central-1`. **`pull` writes corpus. Approval required.** |

## AWS deployment

| Collection | S3 bucket | Bedrock KB (name / ID) | Data source (name / ID) |
|---|---|---|---|
| product-synthesis | `raop-kb-dp-qa-brain-product-synthesis-corpus` | `dp_qa_brain_product_kb` / `PRGABXXNYT` | `dp-qa-brain-product-synthesis-s3` / `H3GLUGV1CX` |
| qa-guidance | `raop-kb-dp-qa-brain-qa-guidance-corpus` | `dp_qa_brain_guidance_kb` / `PLHEYMOXHR` | `dp-qa-brain-qa-guidance-s3` / `HXQVH4AVRL` |

Account `002889194435`, region `eu-central-1`. The bucket layout mirrors `build/<collection>/` exactly (chunk `.md` + `.metadata.json`), so `reconcile_s3.py report` can byte-compare them. Merging a PR does **not** update the KBs: the deployed brain changes only after build → S3 sync → ingestion job.

### AWS access from this workstation

- Use the SSO profile `FullAdminAccessBesidesUserMGMT-002889194435` (sso-session `agentcore`). The `default` profile (`aws login`) expires and needs a browser re-login. If SSO has expired, the user runs `aws sso login --profile FullAdminAccessBesidesUserMGMT-002889194435`.
- Check access with `aws sts get-caller-identity --profile FullAdminAccessBesidesUserMGMT-002889194435`.
- `reconcile_s3.py` hardcodes `PROFILE = "raop-new-account"`, which doesn't exist here. Override it at runtime instead of editing the script:

```powershell
@'
import sys, importlib.util
sys.argv = ["reconcile_s3.py", "report", "--limit", "30"]
spec = importlib.util.spec_from_file_location("r", "scripts/reconcile_s3.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.PROFILE = "FullAdminAccessBesidesUserMGMT-002889194435"
sys.exit(m.main())
'@ | python -
```

Run it from a short-path checkout that has a fresh `build/`, for example `git worktree add --detach C:\dpb_tmp origin/main`, then build, report, and `git worktree remove --force C:\dpb_tmp`.

### Read-only status checks (no approval needed)

```powershell
$p = "FullAdminAccessBesidesUserMGMT-002889194435"
aws bedrock-agent list-ingestion-jobs --knowledge-base-id PRGABXXNYT --data-source-id H3GLUGV1CX --profile $p --region eu-central-1 --sort-by attribute=STARTED_AT,order=DESCENDING --max-results 3
aws bedrock-agent list-ingestion-jobs --knowledge-base-id PLHEYMOXHR --data-source-id HXQVH4AVRL --profile $p --region eu-central-1 --sort-by attribute=STARTED_AT,order=DESCENDING --max-results 3
```

### Deploy (explicit user approval required)

1. Build `origin/main` in a short-path worktree, then run the drift report. Review every `only_in_s3` key. A renamed heading also appears as `only_in_s3`; that's expected, not lost content.
2. `aws s3 sync build/<collection>/ s3://<bucket>/ --delete --profile $p` for each collection.
3. `aws bedrock-agent start-ingestion-job --knowledge-base-id <KB> --data-source-id <DS> --profile $p --region eu-central-1` for each KB, then poll `get-ingestion-job` until `COMPLETE` with `numberOfDocumentsFailed=0`.
4. Re-run the report (expect `TOTAL DRIFT: 0`), then smoke-test through `dp-kb-cognito` (`evaluation_health_check`, plus a 10.15.0.0 query against `dp_qa_brain_product`).

Why `reconcile_s3.py` exists: content once edited directly in S3 (the `05-management-api` and `06-feature-domain` branches) was invisible to the repo and would have been lost on the next sync. **The repo must remain the single source of truth.**

## Building on Windows

`build_corpus.py` fails under `C:\Users\EranP\.vscode\DP_Brain\raop-dp-qa-brain` with `FileNotFoundError`. Some chunk filenames (for example, the PSSLO drop-points section) push paths to about 271 characters, and `LongPathsEnabled=0` on this machine. The script has no output-dir option. A `subst` drive doesn't help because the script calls `Path.resolve()`.

**Option A: short-path copy (verified 2026-10-11, no admin needed)**

```powershell
$t = "C:\dpb_tmp"
robocopy "C:\Users\EranP\.vscode\DP_Brain\raop-dp-qa-brain" $t /E /XD .git build /NFL /NDL /NJH /NJS /NP | Out-Null
Push-Location $t; python scripts/build_corpus.py; python -B scripts/plan_provisioning.py | Select-Object -First 5; Pop-Location
Remove-Item $t -Recurse -Force
```

Result on `78261d6`: 1118 chunks (product-synthesis 75 docs / 833 chunks, qa-guidance 29 docs / 285 chunks).

**Option B: enable Win32 long paths (one-time, admin)**

```powershell
New-ItemProperty -Path HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem -Name LongPathsEnabled -Value 1 -PropertyType DWORD -Force
git config --global core.longpaths true
```

Python 3.6+ honours this setting, so the build then runs in place.

## Definition of done for any brain change

1. `python scripts/validate_corpus.py` reports `Errors: 0. Warnings: 0.`
2. Build succeeds and the chunk counts change as expected.
3. `python scripts/build_feature_catalog.py --check` passes, if `catalog.md` or the alias overrides changed.
4. README / manifest / hub docs are updated for counts, anchors, and new entry points.
5. `build/` is not staged. `git status` shows only intended files.
