# Brain status and known issues

> Snapshot **2026-10-11**, `main` @ `78261d6` (41 commits). Refresh this file whenever the agent runs a health check.

## Health

| Check | Result |
|---|---|
| `validate_corpus.py` | ✅ 102 docs, 11 branches, 41 source IDs, 102 unique IDs, Errors 0, Warnings 0 |
| `build_corpus.py` in place | ❌ `FileNotFoundError`: Windows 260-char path limit (see [pipeline](pipeline.md#building-on-windows)) |
| `build_corpus.py` short path | ✅ 1118 chunks (product 75 docs / 833, guidance 29 docs / 285) |
| `plan_provisioning.py` | ✅ dry-run JSON, `mutations=[]` |
| `reconcile_s3.py report` | ⏸ not run (needs AWS profile `raop-new-account` + `boto3`) |
| Branches | `main` = `origin/brain/releases-10.14-10.15-and-10.16-planned` (merged). Local, unpushed: `brain/readme-anchor-10.15` @ `463f2f1` |

## Known drift inside the brain repo

### Fixed on `brain/readme-anchor-10.15` (awaiting push approval)

- README anchors, counts, branch table, version-family boundary, owner-work items
- `docs/kb-integration.md` smoke criteria and the legacy-fallback description
- `corpus-manifest.json` capacity note
- Anchor and routing text in release-delta, release-inventory, feature-version-map, source-authority, navigation index, 08-parameters router and table map, and the source catalog capacity rows

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
