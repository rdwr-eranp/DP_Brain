# Change log

Changes to the brain (`raop-dp-qa-brain`), its deployed S3/Bedrock knowledge bases, and this workspace. Newest first. Current health and open drift: [docs/brain/status.md](docs/brain/status.md).

## 2026-10-12

### Memory-candidate harvest: default to DefensePro QA team scope

- DynamoDB queue inspection found 1,006 candidates with `scope=team` and `scope_id=ams/defensepro/qa`; the remaining pending records include Cyber Controller and organization-scope entries.
- `harvest_memory_candidates.py` now filters to that exact team scope by default, reports the fetched and retained counts, and includes scope/domain in report metadata. `--scope-id` selects a different team; `--all-scopes` opts out.
- Re-ran the BDoS signature-sync pilot: 296 candidates, all `team:ams/defensepro/qa` and `defensepro`.
- No candidate decisions or DynamoDB writes were made.

## 2026-10-11

### Brain PR #2: restore the release-catalog anchor sentence (merged `bace2c2`, deployed)

- **Problem:** PR #1 reworded the DefensePro X 10.x anchor sentence in `corpus/01-product/release-inventory.md`. The MCP server's `release_catalog.py` (`rdwr-eranp/DP_QA_MCP`) finds that sentence with regexes, so after the PR #1 deploy the live catalog failed with `ReleaseCatalogError: no exact anchor or latest GA release stated for 10.x`, and 10.x version resolution degraded.
- **Fix (`11453e1`):** the same facts in parseable wording: "The exact anchor for 10.x procedures and parameter tables is 10.15.0.0 build 100 …, because the latest DefensePro X GA release is 10.15.0.0 build 100." Verified with the real parser (98 versions, anchors 8.35.5.0 / 10.15.0.0, latest GA 10.15.0.0). Validator: Errors 0.
- **Deploy:** 1 product chunk; ingestion `UREA1VHS7S` COMPLETE (1 modified). `evaluation_health_check` shows `release_catalog.last_error: null`.
- **Lesson:** the parser contract is now documented in [pipeline.md](docs/brain/pipeline.md#deploy-explicit-user-approval-required). Reword those sentences only after testing them with `release_catalog.parse_release_inventory`.

### Brain `bc040d9`: PSSLO required coverage (Guy Perez, merged `7f14132`)

- Connection Limit HTTPS mode and the clear-backend (`-be disable -be-port 80`) case each got their own section in `06-feature-domain/psslo-traffic-statistics-and-cloud-throughput-visibility.md`.
- Deployed outside this workspace. Ingestion jobs: product `IJ0TPDM3PH`, `1SU107WEYQ`; guidance `IB3F5QCQHQ`, `UAD06TRKEQ`. All COMPLETE.

### Brain PR #1: README and anchor fix, 10.13 → 10.15 (merged `9ac1a55`, deployed)

- **Problem:** the brain had been re-grounded to 10.15.0.0, but the README, `docs/kb-integration.md`, the manifest capacity note and several hub documents still named 10.13.0.1 as the anchor.
- **Fix (`463f2f1`, 11 files):**
  - README: anchors, counts, version-family boundary, a branch table covering all 11 branches, Start-here row, owner-work list.
  - `docs/kb-integration.md`: smoke criteria and the legacy-fallback text.
  - `corpus-manifest.json`: capacity note.
  - Anchor and routing text in release-delta, release-inventory, feature-version-map, source-authority-and-versioning, the navigation index, the 08-parameters router and table map, and the source-catalog capacity rows.
- **Deliberately not changed** (needs owner confirmation; see [status.md](docs/brain/status.md#still-open)):
  - the validator-pinned "Exact 10.13 support" README rows;
  - about 90 lines of 10.13 body prose;
  - the "Compared software versions … 10.13.0.1" headers;
  - the `index-10.13.0.1.md` filename.
- **Deploy:** first run of `deploy_brain.py`. 32 object changes (product: 25 changed; guidance: 2 new, 3 changed, 2 deleted, from the renamed source-authority heading). Ingestion: product `FBZXESOXDY` (24 modified), guidance `QHWWFKHXUY` (1 new, 3 modified, 1 deleted). 0 failed.
- **Approved by:** Guy Perez.

### Workspace (this repo)

- Created the DP Brain Maintainer agent, always-on and file-scoped instructions, and the brain and agent docs.
- Documented the AWS side in [pipeline.md](docs/brain/pipeline.md#aws-deployment): buckets, KB and data-source IDs, SSO access, read-only checks, and the deploy procedure.
- Added [scripts/deploy_brain.py](scripts/deploy_brain.py). It byte-compares `build/` with S3 and, with `--apply`, uploads and deletes the changed objects, then starts and polls ingestion only for the KBs that changed. It replaces `aws s3 sync`, which re-uploads every object from a fresh checkout and forces a full re-index.
- Updated the permission matrix, agent constraints and roadmap (new `brain-deploy-kb` skill).

## How to add an entry

For each merged brain PR, note: the problem, the fix commit, what was deliberately left alone, deploy counts, ingestion job IDs, and who approved it. For workspace changes, one line per change. Then refresh [status.md](docs/brain/status.md).
