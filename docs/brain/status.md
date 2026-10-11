# Brain status and known issues

> Snapshot **2026-10-11**, `main` @ `bace2c2` (47 commits). Refresh this file whenever the agent runs a health check. History of changes: [CHANGELOG](../../CHANGELOG.md).

## Health

| Check | Result |
|---|---|
| `validate_corpus.py` | ✅ 102 docs, 11 branches, 41 source IDs, 102 unique IDs, Errors 0, Warnings 0 |
| `build_corpus.py` in place | ❌ `FileNotFoundError`: Windows 260-char path limit (see [pipeline](pipeline.md#building-on-windows)) |
| `build_corpus.py` short path | ✅ 1118 chunks (product 75 docs / 833, guidance 29 docs / 285) |
| `plan_provisioning.py` | ✅ dry-run JSON, `mutations=[]` |
| S3 / KB deployment (2026-10-11, `origin/main` @ `9ac1a55`) | ✅ Deployed with `deploy_brain.py --apply`: 32 object changes (product 25 changed; guidance 2 new, 3 changed, 2 deleted). Ingestion jobs: product `FBZXESOXDY` COMPLETE (24 modified), guidance `QHWWFKHXUY` COMPLETE (1 new, 3 modified, 1 deleted), 0 failed. Re-plan: 0 changes. A live `dp_qa_brain_product` search serves the updated 10.15 parameter router |
| Upstream after deploy (`origin/main` @ `7f14132`, now `bace2c2`) | Guy merged `bc040d9` (PSSLO Connection Limit HTTPS / clear-backend sections). It was deployed outside this workspace: ingestion jobs `IJ0TPDM3PH`/`1SU107WEYQ` (product) and `IB3F5QCQHQ`/`UAD06TRKEQ` (guidance) at 13:46 and 13:48 UTC, all COMPLETE. `deploy_brain.py` plan against `7f14132`: 0 changes. **Another deployer is active.** Coordinate with Guy before each `--apply` |
| MCP release catalog (`evaluation_health_check`) | ✅ PR #1 had broken it for 10.x (`no exact anchor or latest GA release stated for 10.x`). PR #2 (`brain/release-catalog-anchor-sentence`, merged as `bace2c2`) fixed it and was deployed 2026-10-11: 1 chunk, product ingestion `UREA1VHS7S` COMPLETE. Catalog now loads 98 versions, anchors 8.35.5.0 / 10.15.0.0, `last_error: null`; `resolve_version 10.15.0.0` is exact-known |
| Branches | `main` @ `bace2c2`. Merged: `brain/releases-10.14-10.15-and-10.16-planned` (Guy's 10.15 re-ground and PSSLO coverage), PR #1 `brain/readme-anchor-10.15` (`9ac1a55`), PR #2 `brain/release-catalog-anchor-sentence` (`bace2c2`). Both PR branches still exist on the remote and can be deleted |

## Known drift inside the brain repo

### Fixed on `brain/readme-anchor-10.15` (merged 2026-10-11 in PR #1; deployed to S3/KB the same day)

- README anchors, counts, branch table, version-family boundary, owner-work items
- `docs/kb-integration.md` smoke criteria and the legacy-fallback description
- `corpus-manifest.json` capacity note
- Anchor and routing text in release-delta, release-inventory, feature-version-map, source-authority, navigation index, 08-parameters router and table map, and the source catalog capacity rows

### Fixed on `brain/release-catalog-anchor-sentence` (merged 2026-10-11 in PR #2; deployed the same day)

- Restored the 10.x anchor sentence in `release-inventory.md` to a form that `DP_QA_MCP/release_catalog.py` parses. PR #1 had broken the live release catalog for 10.x.

### Still open

1. **Body-prose drift:** about 90 lines in 32 docs with 10.15.0.0 headers still describe facts as "10.13.0.1 …". Many are legitimate history (SNAT introduced in 10.13.0.1, sections "after 10.13.0.1"). The rest need a source-verified pass against the 10.15 UG, RN and CLI. Do not search-and-replace.
2. **README platform lookup and validator pins:** the "Exact 10.13 support" rows and `EXPECTED_README_PLATFORM_ROWS` are the 10.13.0.1 projection. 10.15.0.0 adds X150. Moving them to 10.15 needs owner confirmation and a validator change.
3. **`Compared software versions: 8.35.5.0, 10.13.0.1`** in release-inventory, feature-version-map, platform-codenames, feature-execution-applicability-matrix, upgrade-and-migration-boundaries, and software-upgrade-lifecycle. These are tied to 10.13 RN platform/upgrade facts and are deliberate until those facts are re-grounded.
4. **`08-parameters/index-10.13.0.1.md`** now holds the 10.15.0.0 table map under its old file name. Renaming it changes the S3 key and kbdoc ID, so it needs a coordinated KB update.
5. **`.gitignore`** is the Bitbucket template boilerplate (Node/Java/Maven). Harmless.
6. **`reground_release.py`** hardcodes `C:\raop-workspace\.dp_doc`. That path isn't portable to this machine.

Confirm each item with the owner (Guy Perez) before changing it. Some 10.13 references are deliberate (retained release).

## Open owner-only work (from the brain README / 07-gaps)

1. Release-matched 10.13+/10.15 capacity data (only v10.10.X.X is available)
2. Customer-only known limitations per release
3. Approved 8.x → 10.x migration/conversion procedure (10.0 rejects cross-stream upgrade)
4. Platform installation and maintenance guides (cabling, bypass, boot/recovery, codenames)
5. Exact DME/SME/DPE-by-platform table. Resolve the LACP, public-XVA, and X10/X20 NIC conflicts.
6. Immutable provenance and runtime traces for the `EVENT_PRIORITIES` enums (8.x `DP_HT` condition)
7. Verified bench inventory, entitlements, addresses, certificates, generators, measured rates
8. Requirement-approved rates, thresholds, timing, and pass/fail tolerances
9. Named reviewers for any future `initial → reviewed/approved` promotions

Full registers: [open-questions.md](../../raop-dp-qa-brain/corpus/07-gaps/open-questions.md), [ownership-handoff.md](../../raop-dp-qa-brain/corpus/07-gaps/ownership-handoff.md), and "Sources requiring future extraction" in [source-catalog.md](../../raop-dp-qa-brain/sources/source-catalog.md).
