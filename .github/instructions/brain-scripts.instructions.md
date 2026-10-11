---
description: "Use when modifying the DefensePro QA Brain Python scripts (validate_corpus, build_corpus, plan_provisioning, build_feature_catalog, reground_release, reconcile_s3) or corpus-manifest.json."
applyTo: ["raop-dp-qa-brain/scripts/**/*.py", "raop-dp-qa-brain/corpus-manifest.json"]
---
# Brain scripts

- Keep the scripts standard-library only. Only `reconcile_s3.py` may import `boto3`, and it imports it lazily.
- Validate, build, and plan must make **no network or AWS calls**. `plan_provisioning.py` must keep `execution_mode=dry-run` and `mutations=[]` and write nothing to disk.
- Builds must stay deterministic: same corpus, same `build/` bytes and SHA-256 hashes. Don't add timestamps, random IDs, or order that depends on the filesystem.
- Manifest schema 3 pins exactly two collections (`product-synthesis` → `product_background` / `dp_qa_brain_product_kb`, `qa-guidance` → `test_structure` / `dp_qa_brain_guidance_kb`). Their `directories` lists must exactly cover `corpus/` with no overlap. Branch number prefixes are not collection boundaries.
- If you change an anchor or schema, update `validate_corpus.py`, `corpus-manifest.json`, the brain README, and [docs/kb-integration.md](../../raop-dp-qa-brain/docs/kb-integration.md) in the same change.
- `feature_catalog.json` is generated. Edit `corpus/03-protections/catalog.md` or `feature-alias-overrides.json`, then run `python scripts/build_feature_catalog.py`.
- Verify with `python -m py_compile scripts/*.py`, then the validator, then a short-path build (see `docs/brain/pipeline.md`).
