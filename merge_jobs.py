#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并校招与社招 JSON 为 tencent_jobs.json。"""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "tencent_jobs.json"
CAMPUS = ROOT / "tencent_jobs_campus.json"


def load_jobs(path):
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("jobs", [])


def main():
    campus = load_jobs(CAMPUS)
    social = load_jobs(OUT) if OUT.exists() else []
    # 若 OUT 已是社招全量，social 来自 OUT；campus 来自备份
    if campus and social:
        # 若 OUT 与 campus 备份 id 重叠，以 OUT 中社招为准
        campus_ids = {j["id"] for j in campus}
        social_only = [j for j in social if j.get("source") == "social" or j["id"] not in campus_ids]
        if not social_only and social:
            social_only = social
    else:
        social_only = social

    seen = set()
    merged = []
    for job in campus + social_only:
        jid = job.get("id")
        if jid and jid not in seen:
            seen.add(jid)
            merged.append(job)

    payload = {
        "meta": {
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(merged),
            "campus_count": sum(1 for j in merged if j.get("source") == "campus"),
            "social_count": sum(1 for j in merged if j.get("source") == "social"),
        },
        "jobs": merged,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已合并写入 {OUT}，共 {len(merged)} 条（校招 {payload['meta']['campus_count']} + 社招 {payload['meta']['social_count']}）")


if __name__ == "__main__":
    main()
