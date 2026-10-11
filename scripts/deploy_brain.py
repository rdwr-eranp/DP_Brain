"""Deploy a built DefensePro QA Brain to its S3 buckets and Bedrock knowledge bases.

Byte-compares ``<brain>/build/<collection>/`` with the collection's S3 bucket and then,
only with ``--apply``, uploads changed/new objects, deletes S3-only objects, starts one
ingestion job per changed knowledge base and waits for it to finish.

Unlike ``aws s3 sync``, it never re-uploads identical content, so a fresh checkout does
not force Bedrock to re-index every chunk.

    python scripts/deploy_brain.py --brain C:\\dpb_tmp            # plan only (read-only)
    python scripts/deploy_brain.py --brain C:\\dpb_tmp --apply    # upload + delete + ingest

``--apply`` mutates cloud resources: run it only with explicit user approval.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

REGION = "eu-central-1"
DEFAULT_PROFILE = "FullAdminAccessBesidesUserMGMT-002889194435"
COLLECTIONS = {
    "product-synthesis": {
        "bucket": "raop-kb-dp-qa-brain-product-synthesis-corpus",
        "kb": "PRGABXXNYT",
        "data_source": "H3GLUGV1CX",
    },
    "qa-guidance": {
        "bucket": "raop-kb-dp-qa-brain-qa-guidance-corpus",
        "kb": "PLHEYMOXHR",
        "data_source": "HXQVH4AVRL",
    },
}
CONTENT_TYPES = {".md": "text/markdown", ".json": "application/json"}


def s3_objects(s3, bucket: str) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket):
        for item in page.get("Contents", []):
            out[item["Key"]] = s3.get_object(Bucket=bucket, Key=item["Key"])["Body"].read()
    return out


def local_objects(root: pathlib.Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def plan(s3, brain: pathlib.Path) -> dict[str, dict[str, list[str]]]:
    result = {}
    for name, cfg in COLLECTIONS.items():
        root = brain / "build" / name
        if not root.is_dir():
            sys.exit(f"missing {root}; run build_corpus.py in {brain} first")
        local, remote = local_objects(root), s3_objects(s3, cfg["bucket"])
        result[name] = {
            "upload_new": sorted(set(local) - set(remote)),
            "upload_changed": sorted(k for k in set(local) & set(remote) if local[k] != remote[k]),
            "delete": sorted(set(remote) - set(local)),
        }
    return result


def apply(s3, brain: pathlib.Path, changes: dict[str, list[str]], name: str) -> None:
    bucket, root = COLLECTIONS[name]["bucket"], brain / "build" / name
    for key in changes["upload_new"] + changes["upload_changed"]:
        content_type = CONTENT_TYPES.get(pathlib.PurePosixPath(key).suffix, "application/octet-stream")
        s3.put_object(Bucket=bucket, Key=key, Body=(root / key).read_bytes(),
                      ContentType=content_type, ServerSideEncryption="AES256")
    for key in changes["delete"]:
        s3.delete_object(Bucket=bucket, Key=key)


def ingest(agent, name: str, timeout_s: int) -> dict:
    cfg = COLLECTIONS[name]
    job = agent.start_ingestion_job(knowledgeBaseId=cfg["kb"], dataSourceId=cfg["data_source"],
                                    description="deploy_brain.py")["ingestionJob"]
    deadline = time.time() + timeout_s
    while job["status"] in ("STARTING", "IN_PROGRESS") and time.time() < deadline:
        time.sleep(10)
        job = agent.get_ingestion_job(knowledgeBaseId=cfg["kb"], dataSourceId=cfg["data_source"],
                                      ingestionJobId=job["ingestionJobId"])["ingestionJob"]
    return job


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--brain", required=True, type=pathlib.Path, help="brain checkout with a fresh build/")
    parser.add_argument("--profile", default=DEFAULT_PROFILE)
    parser.add_argument("--apply", action="store_true", help="upload, delete and ingest (needs approval)")
    parser.add_argument("--timeout", type=int, default=1800, help="seconds to wait per ingestion job")
    args = parser.parse_args()

    import boto3

    session = boto3.Session(profile_name=args.profile, region_name=REGION)
    s3, agent = session.client("s3"), session.client("bedrock-agent")
    brain = args.brain.resolve()
    changes = plan(s3, brain)

    total = 0
    for name, c in changes.items():
        total += sum(len(v) for v in c.values())
        print(f"== {name} -> s3://{COLLECTIONS[name]['bucket']}  "
              f"new={len(c['upload_new'])} changed={len(c['upload_changed'])} delete={len(c['delete'])}")
        for kind, keys in c.items():
            for key in keys:
                print(f"   {kind:15} {key}")
    print(f"TOTAL CHANGES: {total}")

    if not args.apply:
        print("Plan only; nothing changed.")
        return 0
    if total == 0:
        print("Already in sync; nothing to ingest.")
        return 0

    failed = False
    for name, c in changes.items():
        if not any(c.values()):
            continue
        apply(s3, brain, c, name)
        job = ingest(agent, name, args.timeout)
        stats = {k: v for k, v in job.get("statistics", {}).items() if v}
        print(f"== {name} ingestion {job['ingestionJobId']}: {job['status']} {json.dumps(stats)}")
        failed |= job["status"] != "COMPLETE" or stats.get("numberOfDocumentsFailed", 0) > 0
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
