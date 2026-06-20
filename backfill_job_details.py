#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回填 tencent_jobs.json 中缺失的岗位职责/任职要求。

仅对 responsibility 或 requirement 为空的岗位，从腾讯官方 API 拉取详情并补全。
"""

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from scrape_tencent_jobs import (
    OUTPUT,
    extract_campus_responsibility,
    extract_campus_requirement,
    extract_skills_from_text,
    fetch_campus_detail,
    fetch_social_detail,
    normalize_text,
)

WORKERS = 12


def needs_backfill(job):
    """判断岗位是否缺少职责或任职要求。"""
    return not job.get("responsibility") or not job.get("requirement")


def apply_detail_to_job(job, detail):
    """
    用 API 详情补全岗位的空字段，并刷新 desc / tags。

    仅更新原本为空的 responsibility / requirement，不覆盖已有内容。
    """
    if not detail:
        return False

    project = job.get("project") or detail.get("projectName", "")
    updated = False

    if not job.get("responsibility"):
        resp = extract_campus_responsibility(detail) if job.get("source") == "campus" else normalize_text(
            detail.get("Responsibility", "")
        )
        if resp:
            job["responsibility"] = resp
            updated = True

    if not job.get("requirement"):
        if job.get("source") == "campus":
            req = extract_campus_requirement(detail, project)
        else:
            req = normalize_text(detail.get("Requirement", ""))
        if req:
            job["requirement"] = req
            updated = True

    if updated:
        resp = job.get("responsibility", "")
        req = job.get("requirement", "")
        job["desc"] = resp[:120] + ("…" if len(resp) > 120 else "")
        job["tags"] = extract_skills_from_text(req + " " + job.get("title", ""))

    return updated


def fetch_detail_for_job(job):
    """按岗位来源拉取官方详情。"""
    post_id = job.get("id")
    if not post_id:
        return None, "missing_id"

    if job.get("source") == "campus":
        detail = fetch_campus_detail(post_id)
        if detail is None:
            return None, "api_no_data"
        return detail, None

    if job.get("source") == "social":
        detail = fetch_social_detail(post_id)
        if detail is None:
            return None, "api_no_data"
        return detail, None

    return None, "unknown_source"


def backfill_jobs(jobs, workers=WORKERS):
    """
    并发回填缺失字段。

    返回 (filled_count, still_empty, failures)。
    """
    targets = [(i, j) for i, j in enumerate(jobs) if needs_backfill(j)]
    if not targets:
        return 0, [], []

    filled = 0
    failures = []
    still_empty_after = []

    def task(idx_job):
        idx, job = idx_job
        detail, err = fetch_detail_for_job(job)
        if err:
            return idx, job, False, err
        ok = apply_detail_to_job(job, detail)
        if not ok:
            return idx, job, False, "no_text_in_api"
        return idx, job, True, None

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(task, t): t for t in targets}
        done = 0
        for fut in as_completed(futures):
            done += 1
            if done % 50 == 0:
                print(f"  进度 {done}/{len(targets)}")
            try:
                idx, job, ok, err = fut.result()
                if ok:
                    filled += 1
                else:
                    failures.append({"id": job.get("id"), "title": job.get("title"), "reason": err})
                    if needs_backfill(job):
                        still_empty_after.append(job)
            except Exception as e:
                idx, job = futures[fut]
                failures.append({"id": job.get("id"), "title": job.get("title"), "reason": str(e)})
                if needs_backfill(job):
                    still_empty_after.append(job)

    return filled, still_empty_after, failures


def main():
    """加载 JSON、回填、保存并打印统计。"""
    path = OUTPUT
    if not path.exists():
        print(f"未找到 {path}", file=sys.stderr)
        sys.exit(1)

    payload = json.loads(path.read_text(encoding="utf-8"))
    jobs = payload.get("jobs", [])
    before_empty = sum(1 for j in jobs if needs_backfill(j))
    print(f"共 {len(jobs)} 条岗位，需回填 {before_empty} 条")

    filled, still_empty, failures = backfill_jobs(jobs)

    after_empty = sum(1 for j in jobs if needs_backfill(j))
    payload["meta"]["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n回填完成：成功补全 {filled} 条")
    print(f"仍缺失职责/要求：{after_empty} 条")
    if failures:
        print("\n未能补全（API 无数据或岗位已下架）：")
        for f in failures[:20]:
            print(f"  - {f['id']} | {f['title'][:40]} | {f['reason']}")
        if len(failures) > 20:
            print(f"  … 另有 {len(failures) - 20} 条")

    return filled, after_empty


if __name__ == "__main__":
    main()
