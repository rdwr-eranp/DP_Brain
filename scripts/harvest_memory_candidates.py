"""Read-only harvest of RAOP governed-memory candidates for brain review.

Pulls candidates from the DynamoDB table ``raop-prod-memory-governance`` through
the ``review-queue-index`` GSI (Query only), or from a previously saved JSON
export, then groups them for one feature and triages them against the brain:

* parses "planning question ... Validated owner answer: ..." content;
* classifies every cited ID as a brain document, a catalogued source, an ID
  already mentioned in the corpus, or unknown to the brain;
* clusters near-duplicate questions;
* checks that quoted section names in an answer exist as headings in the
  feature's brain document.

It never writes to DynamoDB. Decisions on candidates go through the RAOP
memory-governance REST API, never through this script.

Examples:
    python scripts/harvest_memory_candidates.py --list-features
    python scripts/harvest_memory_candidates.py --feature bdos-signature-sync
    python scripts/harvest_memory_candidates.py --from-json cands.json --feature snat
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import sys
from pathlib import Path

REGION = "eu-central-1"
DEFAULT_PROFILE = "FullAdminAccessBesidesUserMGMT-002889194435"
TABLE = "raop-prod-memory-governance"
INDEX = "review-queue-index"
ROOT = Path(__file__).resolve().parent.parent

# Candidate feature tags are free text; several spellings name one feature.
FEATURE_ALIASES = {
    "bdos-signature-sync": r"bdos.*sig.*sync|sig.*sync.*bdos",
    "snat": r"\bsnat\b",
    "psslo": r"psslo",
    "pqc-support": r"\bpqc\b",
    "cloud-mcp-protection": r"cloud.?mcp",
    "cpu-suppression": r"cpu.?suppression",
    "webddos-quic": r"webddos.*quic|quic.*webddos",
    "l4-hash-distribution": r"l4.*hash",
    "frd": r"\bfrd\b",
    "reporting-100k-entries": r"reporting.*100k",
    "event-exporter-extension": r"event.?exporter",
}

QA_RE = re.compile(
    r"^For feature (?P<feature>.+?), planning question (?P<qid>\S+?):\s*(?P<head>.*?)"
    r"(?:\n\s*In question:\s*(?P<question>.*?))?\s*\n\s*Validated owner answer:\s*(?P<answer>.*)$",
    re.S,
)
ID_RE = re.compile(r"\bDP-(?:[A-Z][A-Z0-9]*-)+[A-Z0-9.]*\d[A-Z0-9.]*\b|\bDP-\d{5,}\b")
QUOTED_RE = re.compile(r"'([A-Z][^'\n]{3,80})'")
WORD_RE = re.compile(r"[a-z0-9]+")
STOP = set("the a an of to and or is are be in on for with that this it as by at from not no does do any".split())


def feature_of(cand: dict) -> list[str]:
    return [t.split(":", 1)[1] for t in cand.get("trigger_terms", []) if t.startswith("feature:")]


def canonical_feature(tag: str) -> str:
    low = tag.lower()
    for slug, pattern in FEATURE_ALIASES.items():
        if re.search(pattern, low):
            return slug
    return re.sub(r"[^a-z0-9]+", "-", low).strip("-")


def load_live(profile: str, status: str) -> list[dict]:
    import boto3

    table = boto3.Session(profile_name=profile, region_name=REGION).resource("dynamodb").Table(TABLE)
    out, key = [], None
    while True:
        kw = {
            "IndexName": INDEX,
            "KeyConditionExpression": "review_status = :s",
            "ExpressionAttributeValues": {":s": status},
        }
        if key:
            kw["ExclusiveStartKey"] = key
        page = table.query(**kw)
        out += [json.loads(i["record_json"]) for i in page["Items"] if i.get("sk") == "CURRENT"]
        key = page.get("LastEvaluatedKey")
        if not key:
            return out


def brain_index(brain: Path) -> dict:
    docs, mentioned, headings_by_doc, doc_paths = set(), set(), {}, {}
    for path in (brain / "corpus").rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"Document ID:\s*\**\s*(DP-[A-Z0-9.-]+)", text)
        if m:
            docs.add(m.group(1))
            doc_paths[m.group(1)] = path
            headings_by_doc[m.group(1)] = {
                h.strip().strip("#").strip().lower() for h in re.findall(r"^#{1,4} .+$", text, re.M)
            }
        mentioned.update(ID_RE.findall(text))
    catalog = brain / "sources" / "source-catalog.md"
    sources = set(re.findall(r"^## (\S+)", catalog.read_text(encoding="utf-8"), re.M)) if catalog.exists() else set()
    return {"docs": docs, "sources": sources, "mentioned": mentioned, "headings": headings_by_doc, "paths": doc_paths}


def classify_ids(ids: set[str], idx: dict) -> dict[str, list[str]]:
    out = collections.defaultdict(list)
    for i in sorted(ids):
        if i in idx["docs"]:
            out["brain_doc"].append(i)
        elif i in idx["sources"]:
            out["catalogued_source"].append(i)
        elif i in idx["mentioned"]:
            out["mentioned_in_corpus"].append(i)
        else:
            out["unknown_to_brain"].append(i)
    return dict(out)


def tokens(text: str) -> set[str]:
    return {w for w in WORD_RE.findall(text.lower()) if w not in STOP and len(w) > 2}


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def triage(cands: list[dict], idx: dict, feature_doc: str | None) -> list[dict]:
    rows = []
    for c in cands:
        text = c.get("original_content") or c.get("proposed_canonical_content") or ""
        m = QA_RE.match(text)
        question = answer = None
        if m:
            question = (m.group("question") or m.group("head") or "").strip()
            answer = m.group("answer").strip()
        ids = classify_ids(set(ID_RE.findall(text)), idx)
        missing_sections = []
        if feature_doc and answer and feature_doc in ids.get("brain_doc", []):
            heads = idx["headings"].get(feature_doc, set())
            for q in QUOTED_RE.findall(answer):
                ql = q.lower()
                if not any(ql in h or h in ql for h in heads):
                    missing_sections.append(q)
        if c.get("candidate_type") != "validated_operational_rule" or not m:
            bucket = "instruction"
        elif ids.get("unknown_to_brain"):
            bucket = "new-reference"
        elif ids:
            bucket = "brain-grounded"
        else:
            bucket = "uncited"
        rows.append({
            "candidate_id": c["candidate_id"],
            "type": c.get("candidate_type"),
            "owner": c.get("owner_id"),
            "scope": c.get("scope"),
            "scope_id": c.get("scope_id"),
            "domain": c.get("domain"),
            "created_at": c.get("created_at"),
            "question_id": m.group("qid") if m else None,
            "issue": (m.group("head").strip() if m and m.group("question") else None),
            "question": question,
            "answer": answer,
            "content": None if m else text,
            "ids": ids,
            "missing_sections": missing_sections,
            "conflicts": len(c.get("conflict_ids") or []),
            "nearest": len(c.get("nearest_matches") or []),
            "evidence_quality": c.get("evidence_quality_score"),
            "observations": len(c.get("observation_ids") or []),
            "bucket": bucket,
        })
    return rows


def cluster(rows: list[dict], threshold: float) -> list[list[dict]]:
    clusters: list[tuple[set[str], list[dict]]] = []
    for r in sorted(rows, key=lambda r: r["created_at"] or ""):
        key = tokens(r["question"] or r["content"] or "")
        for ckey, members in clusters:
            if members[0]["bucket"] == r["bucket"] and jaccard(key, ckey) >= threshold:
                members.append(r)
                break
        else:
            clusters.append((key, [r]))
    return [m for _, m in clusters]


def clip(text: str | None, n: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[: n - 1] + "…"


def write_report(path: Path, feature: str, feature_doc: str | None, rows: list[dict], clusters: list[list[dict]]) -> None:
    by_bucket = collections.Counter(r["bucket"] for r in rows)
    by_scope = collections.Counter(f"{r['scope']}:{r['scope_id']}" for r in rows)
    by_domain = collections.Counter(r["domain"] for r in rows)
    unknown = collections.Counter(i for r in rows for i in r["ids"].get("unknown_to_brain", []))
    missing = collections.Counter(s for r in rows for s in r["missing_sections"])
    lines = [
        f"# Memory-candidate harvest: {feature}",
        "",
        f"Generated {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC, read-only from `{TABLE}`.",
        f"Brain feature document: `{feature_doc or 'none found'}`.",
        "",
        "Candidates are unreviewed owner answers captured during test-plan generation. They are leads",
        "for brain review, not citable facts. Nothing here was written back to the governance table.",
        "",
        "## Summary",
        "",
        f"- Candidates: {len(rows)}; question clusters: {len(clusters)}",
        f"- Scope: " + (", ".join(f"{k} ({v})" for k, v in by_scope.most_common()) or "none"),
        f"- Domain: " + (", ".join(f"{k} ({v})" for k, v in by_domain.most_common()) or "none"),
        f"- Buckets: " + ", ".join(f"{k} {v}" for k, v in by_bucket.most_common()),
        f"- With conflicts: {sum(1 for r in rows if r['conflicts'])}; with nearest matches: {sum(1 for r in rows if r['nearest'])}",
        f"- IDs unknown to the brain: " + (", ".join(f"{i} ({n})" for i, n in unknown.most_common()) or "none"),
        f"- Quoted sections not found in the feature document: "
        + (", ".join(f"'{s}' ({n})" for s, n in missing.most_common()) or "none"),
        "",
        "Bucket meaning:",
        "",
        "- **new-reference**: the answer cites an ID the brain has never seen; it needs a source entry before use.",
        "- **uncited**: an owner assertion with no reference; it needs owner confirmation and a source.",
        "- **brain-grounded**: cites only brain documents, catalogued sources or IDs already in the corpus; check for drift.",
        "- **instruction**: reviewer instructions or corrections; candidates for qa-guidance rules.",
        "",
    ]
    order = ["new-reference", "uncited", "brain-grounded", "instruction"]
    for bucket in order:
        group = [c for c in clusters if c[0]["bucket"] == bucket]
        if not group:
            continue
        lines += [f"## {bucket} ({len(group)} clusters)", ""]
        for n, members in enumerate(sorted(group, key=len, reverse=True), 1):
            rep = members[-1]
            ids = sorted({i for m in members for v in m["ids"].values() for i in v})
            flags = []
            if any(m["conflicts"] for m in members):
                flags.append("conflict")
            if any(m["missing_sections"] for m in members):
                flags.append("missing-section")
            lines += [
                f"### {bucket}-{n}: {len(members)} candidate(s)" + (f" [{', '.join(flags)}]" if flags else ""),
                "",
            ]
            if rep["question"]:
                lines.append(f"- **Question:** {clip(rep['question'], 400)}")
                lines.append(f"- **Latest answer:** {clip(rep['answer'], 900)}")
            else:
                lines.append(f"- **Content:** {clip(rep['content'], 900)}")
            if ids:
                lines.append(f"- **Cited:** {', '.join(ids)}")
            lines.append(f"- **Candidates:** {', '.join(m['candidate_id'] for m in members)}")
            lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def find_feature_doc(idx: dict, feature: str) -> str | None:
    for doc_id, path in idx["paths"].items():
        if path.stem == feature:
            return doc_id
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile", default=DEFAULT_PROFILE)
    ap.add_argument("--status", default="pending", help="review_status to read (default: pending)")
    ap.add_argument("--from-json", type=Path, help="use a saved export instead of DynamoDB")
    ap.add_argument("--save-json", type=Path, help="save the filtered export (keep it out of git)")
    ap.add_argument(
        "--scope-id",
        default="ams/defensepro/qa",
        help="include only this team scope ID (default: ams/defensepro/qa)",
    )
    ap.add_argument("--all-scopes", action="store_true", help="include candidates outside the default team scope")
    ap.add_argument("--feature", help="canonical feature slug, e.g. bdos-signature-sync")
    ap.add_argument("--list-features", action="store_true")
    ap.add_argument("--brain", type=Path, default=ROOT / "raop-dp-qa-brain")
    ap.add_argument("--out", type=Path, default=ROOT / "out" / "memory-harvest")
    ap.add_argument("--threshold", type=float, default=0.55, help="question-clustering Jaccard threshold")
    args = ap.parse_args()

    cands = json.loads(args.from_json.read_text(encoding="utf-8")) if args.from_json else load_live(args.profile, args.status)
    fetched_count = len(cands)
    if not args.all_scopes:
        cands = [
            c for c in cands
            if c.get("scope") == "team" and c.get("scope_id") == args.scope_id
        ]
    if args.save_json:
        args.save_json.write_text(json.dumps(cands, ensure_ascii=False), encoding="utf-8")
    scope_label = "all scopes" if args.all_scopes else f"team scope {args.scope_id}"
    print(f"{len(cands)} candidates ({args.status}; {scope_label}; fetched {fetched_count})")

    by_feature = collections.defaultdict(list)
    for c in cands:
        for slug in {canonical_feature(t) for t in feature_of(c)} or {"(none)"}:
            by_feature[slug].append(c)

    if args.list_features or not args.feature:
        for slug, items in sorted(by_feature.items(), key=lambda kv: -len(kv[1])):
            print(f"{len(items):5d}  {slug}")
        return 0

    selected = by_feature.get(args.feature, [])
    if not selected:
        print(f"no candidates for feature {args.feature!r}", file=sys.stderr)
        return 1
    idx = brain_index(args.brain)
    feature_doc = find_feature_doc(idx, args.feature)
    rows = triage(selected, idx, feature_doc)
    clusters = cluster(rows, args.threshold)

    args.out.mkdir(parents=True, exist_ok=True)
    report = args.out / f"{args.feature}.md"
    write_report(report, args.feature, feature_doc, rows, clusters)
    (args.out / f"{args.feature}.json").write_text(
        json.dumps({"feature": args.feature, "feature_doc": feature_doc, "rows": rows}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"{len(rows)} candidates, {len(clusters)} clusters -> {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
