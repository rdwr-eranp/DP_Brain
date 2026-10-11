---
description: "Use when creating or editing DefensePro QA Brain corpus documents or the source catalog: document header fields, Document ID scheme, applicability scope, section pattern, citations, review status, 8.x vs 10.x family rules."
applyTo: ["raop-dp-qa-brain/corpus/**/*.md", "raop-dp-qa-brain/sources/**/*.md"]
---
# Brain corpus authoring

The authority is [authoring-guide.md](../../raop-dp-qa-brain/docs/authoring-guide.md). The validator ([validate_corpus.py](../../raop-dp-qa-brain/scripts/validate_corpus.py)) enforces most of these rules.

## Header (first lines of every corpus file)

```text
Document ID: DP-QA-<AREA>[-<TOPIC>]-<NNN>
Product: DefensePro
Applicability: <version/platform/mode scope>
Applicability scope: exact-release | release-family | cross-family | version-agnostic
Product line: DefensePro 8 | DefensePro X | DefensePro 8 and DefensePro X
Software version: N.N.N.N            # exact-release only
Compared software versions: A, B     # cross-family only; must cover majors 8 and 10
Authority: <product source or curated QA status>
Status: initial | reviewed | approved | deprecated
Owner: <name or TBD>                 # reviewed/approved cannot be TBD
Last reviewed: YYYY-MM-DD

Purpose: <one sentence>
```

- `Applicability scope` and `Product line` are mandatory for new product-synthesis docs (01, 02, 03, 04, 05-management-api, 06-feature-domain, 08).
- Area codes in use: `NAV`, `PROD`, `CONF`, `PROT`, `ATTACK`, `LAB`, `API`, `FEAT`, `WF`, `GAP`, `PARAM`. Before you pick a number, search for `^Document ID: DP-QA-<AREA>` so the ID is unique.
- New docs start as `Status: initial`. Changing the status needs a named reviewer from the user.
- Keep the header short. Generated `.metadata.json` sidecars must stay at or under 1,024 bytes, so avoid long `Applicability` or `Owner` strings.

## Body

- One stable topic per file. Each H2 must make sense when retrieved alone, so repeat the feature/object name in the H2 heading and opening sentence.
- Keep each section under about 3,000 characters. The builder splits longer sections, and the planner reads 3,000-character excerpts.
- Separate **Product facts**, **QA implications**, **TBD / prohibited inference**, and **Sources**.
- Product-synthesis docs need a non-empty `## Sources` H2 whose `source://<ID>` references all exist in [source-catalog.md](../../raop-dp-qa-brain/sources/source-catalog.md).
- Use relative Markdown links only. No machine-local absolute paths.
- Never infer rates, thresholds, timers, defaults, commands, OIDs, endpoints, or hardware placement. Write `TBD` and link it to [open-questions.md](../../raop-dp-qa-brain/corpus/07-gaps/open-questions.md).
- FPGA or EZchip mentions need an explicit evidence boundary.
- Configuration order: `global -> classes/prerequisites -> profile -> enabled policy/binding -> apply/activate -> confirm in effect -> behavior assertion`.

## After editing

Run `python scripts/validate_corpus.py` from `raop-dp-qa-brain/` and fix everything until it reports `Errors: 0`.
