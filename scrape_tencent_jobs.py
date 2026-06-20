#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯招聘岗位爬虫（本地运行，无需付费服务）

数据源：
1. join.qq.com 校招岗位（post.html）— searchPosition + getJobDetailsByPostId
2. careers.tencent.com 社招岗位 — Query 列表 + ByPostId 详情

输出：tencent_jobs.json
"""

import json
import re
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

OUTPUT = Path(__file__).parent / "tencent_jobs.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
}
JOIN_REFERER = {"Referer": "https://join.qq.com/post.html"}
CAREERS_REFERER = {"Referer": "https://careers.tencent.com/"}


def http_get(url, extra_headers=None, retries=3):
    """发起 GET 请求并解析 JSON。"""
    headers = {**HEADERS, **(extra_headers or {})}
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if i == retries - 1:
                raise
            time.sleep(0.5 * (i + 1))


def http_post_json(url, payload, extra_headers=None, retries=3):
    """发起 POST JSON 请求。"""
    headers = {
        **HEADERS,
        "Content-Type": "application/json",
        **(extra_headers or {}),
    }
    data = json.dumps(payload).encode("utf-8")
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if i == retries - 1:
                raise
            time.sleep(0.5 * (i + 1))


def normalize_text(text):
    """清洗文本中的换行与多余空白。"""
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text).replace("\r\n", "\n").replace("\r", "\n")).strip()


def extract_skills_from_text(text):
    """从任职要求文本中提取技能关键词（供前端匹配复用）。"""
    if not text:
        return []
    keywords = [
        "Java", "Python", "Go", "C++", "C#", "JavaScript", "TypeScript", "React", "Vue",
        "MySQL", "Redis", "SQL", "算法", "机器学习", "深度学习", "数据分析", "产品设计",
        "UI", "UX", "运营", "市场", "Linux", "Kubernetes", "Docker", "分布式", "微服务",
        "NLP", "CV", "TensorFlow", "PyTorch", "Spark", "Hadoop", "Flutter", "iOS", "Android",
        "LLM", "RAG", "AIGC", "LangChain", "大模型", "Prompt", "Agent", "Transformer",
        "ChatGPT", "Claude", "Copilot", "Midjourney", "Stable Diffusion",
    ]
    found = []
    lower = text.lower()
    for kw in keywords:
        if kw.lower() in lower or kw in text:
            found.append(kw)
    return list(dict.fromkeys(found))[:12]


# ---------- join.qq.com 校招 ----------

def fetch_campus_list():
    """拉取校招岗位列表。"""
    url = "https://join.qq.com/api/v1/position/searchPosition"
    # 单次可返回全部 534 条
    data = http_post_json(url, {"pageIndex": 1, "pageSize": 600}, JOIN_REFERER)
    if data.get("status") != 0:
        raise RuntimeError(f"校招列表接口异常: {data}")
    return data["data"]["positionList"]


def fetch_campus_detail(post_id):
    """按 postId 获取校招岗位详情。"""
    url = f"https://join.qq.com/api/v1/jobDetails/getJobDetailsByPostId?postId={post_id}"
    data = http_get(url, JOIN_REFERER)
    if data.get("status") != 0:
        return None
    return data.get("data")


def extract_campus_responsibility(detail):
    """从校招详情 API 提取岗位职责/课题描述（官网原文，按字段优先级）。"""
    d = detail or {}
    return normalize_text(
        d.get("desc")
        or d.get("topicDetail")
        or d.get("introduction")
        or ""
    )


def extract_campus_requirement(detail, project_name=""):
    """从校招详情 API 提取任职要求/课题要求（官网原文，按字段优先级）。"""
    d = detail or {}
    direct = d.get("request") or d.get("topicRequirement")
    if direct:
        return normalize_text(direct)
    if project_name == "应届毕业生":
        return normalize_text(d.get("graduateBonus") or d.get("internBonus") or "")
    return normalize_text(d.get("internBonus") or d.get("graduateBonus") or "")


def map_campus_job(item, detail):
    """将校招数据映射为统一结构。"""
    post_id = item.get("postId") or (detail or {}).get("postId")
    title = (detail or {}).get("title") or item.get("positionTitle", "")
    dept_parts = []
    if item.get("bgs"):
        dept_parts.append(item["bgs"].strip())
    if item.get("projectName"):
        dept_parts.append(item["projectName"])
    department = " · ".join(dept_parts) if dept_parts else "腾讯"
    cities = []
    if detail and detail.get("workCityList"):
        cities = detail["workCityList"]
    elif item.get("workCities"):
        cities = [c.strip() for c in item["workCities"].split() if c.strip()]
    location = cities[0] if cities else "不限"
    project_name = item.get("projectName", "") or (detail or {}).get("projectName", "")
    responsibility = extract_campus_responsibility(detail)
    requirement = extract_campus_requirement(detail, project_name)
    category = (detail or {}).get("tidName") or item.get("recruitLabelName", "")
    return {
        "id": str(post_id),
        "title": title,
        "department": f"腾讯 · {department}",
        "location": location,
        "locations": cities,
        "category": category,
        "project": item.get("projectName", ""),
        "responsibility": responsibility,
        "requirement": requirement,
        "published_at": "",
        "source": "campus",
        "url": f"https://join.qq.com/post_detail.html?postid={post_id}",
        "tags": extract_skills_from_text(requirement + " " + title),
        "desc": responsibility[:120] + ("…" if len(responsibility) > 120 else ""),
    }


def scrape_campus_jobs(workers=12):
    """爬取全部校招岗位。"""
    print("正在获取校招岗位列表…")
    items = fetch_campus_list()
    print(f"校招列表共 {len(items)} 条，开始拉取详情…")

    def task(item):
        post_id = item.get("postId")
        if not post_id:
            return None
        detail = fetch_campus_detail(post_id)
        return map_campus_job(item, detail)

    jobs = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(task, it): it for it in items}
        done = 0
        for fut in as_completed(futures):
            done += 1
            if done % 50 == 0:
                print(f"  校招详情进度 {done}/{len(items)}")
            try:
                job = fut.result()
                if job and job.get("title"):
                    jobs.append(job)
            except Exception as e:
                print(f"  跳过一条校招: {e}")
    print(f"校招完成: {len(jobs)} 条")
    return jobs


# ---------- careers.tencent.com 社招 ----------

def fetch_social_list_page(page_index, page_size=100):
    """拉取社招列表单页。"""
    url = (
        "https://careers.tencent.com/tencentcareer/api/post/Query"
        f"?pageIndex={page_index}&pageSize={page_size}&language=zh-cn&area=cn"
    )
    data = http_get(url, CAREERS_REFERER)
    if data.get("Code") != 200:
        raise RuntimeError(f"社招列表异常 page={page_index}: {data}")
    return data["Data"]


def fetch_social_detail(post_id):
    """拉取社招岗位详情（含任职要求）。"""
    url = f"https://careers.tencent.com/tencentcareer/api/post/ByPostId?postId={post_id}"
    data = http_get(url, CAREERS_REFERER)
    if data.get("Code") != 200:
        return None
    return data.get("Data")


def map_social_job(item, detail=None):
    """将社招数据映射为统一结构。"""
    d = detail or item
    post_id = str(d.get("PostId") or item.get("PostId", ""))
    title = d.get("RecruitPostName", "")
    bg = d.get("BGName", "")
    product = d.get("ProductName", "")
    dept = " · ".join(filter(None, [bg, product]))
    location = d.get("LocationName", "不限")
    responsibility = normalize_text(d.get("Responsibility", ""))
    requirement = normalize_text(d.get("Requirement", ""))
    category = d.get("CategoryName", "")
    return {
        "id": post_id,
        "title": title,
        "department": f"腾讯 · {dept}" if dept else "腾讯",
        "location": location,
        "locations": [location] if location else [],
        "category": category,
        "project": product or "",
        "responsibility": responsibility,
        "requirement": requirement,
        "published_at": d.get("LastUpdateTime", ""),
        "source": "social",
        "url": d.get("PostURL") or f"https://careers.tencent.com/jobdesc.html?postId={post_id}",
        "tags": extract_skills_from_text((requirement or "") + " " + (responsibility or "") + " " + title),
        "desc": responsibility[:120] + ("…" if len(responsibility) > 120 else ""),
    }


def scrape_social_jobs(workers=16, fetch_detail=True):
    """爬取全部社招岗位。"""
    print("正在获取社招岗位列表…")
    first = fetch_social_list_page(1, 100)
    total = first.get("Count", 0)
    page_size = 100
    total_pages = (total + page_size - 1) // page_size
    all_posts = list(first.get("Posts", []))

    for p in range(2, total_pages + 1):
        data = fetch_social_list_page(p, page_size)
        all_posts.extend(data.get("Posts", []))
        print(f"  社招列表页 {p}/{total_pages}")
        time.sleep(0.15)

    print(f"社招列表共 {len(all_posts)} 条")

    if not fetch_detail:
        return [map_social_job(p) for p in all_posts if p.get("RecruitPostName")]

    def task(post):
        post_id = post.get("PostId")
        detail = fetch_social_detail(post_id) if post_id else None
        return map_social_job(post, detail or post)

    jobs = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(task, p): p for p in all_posts}
        done = 0
        for fut in as_completed(futures):
            done += 1
            if done % 100 == 0:
                print(f"  社招详情进度 {done}/{len(all_posts)}")
            try:
                job = fut.result()
                if job and job.get("title"):
                    jobs.append(job)
            except Exception as e:
                print(f"  跳过一条社招: {e}")
    print(f"社招完成: {len(jobs)} 条")
    return jobs


def main():
    """主流程：爬取并写入 JSON。"""
    import argparse
    parser = argparse.ArgumentParser(description="爬取腾讯招聘岗位")
    parser.add_argument("--campus-only", action="store_true", help="仅爬校招 join.qq.com")
    parser.add_argument("--social-only", action="store_true", help="仅爬社招 careers.tencent.com")
    parser.add_argument("--no-social-detail", action="store_true", help="社招不拉详情（更快但无任职要求）")
    args = parser.parse_args()

    jobs = []
    if not args.social_only:
        jobs.extend(scrape_campus_jobs())
    if not args.campus_only:
        jobs.extend(scrape_social_jobs(fetch_detail=not args.no_social_detail))

    # 去重（按 id）
    seen = set()
    unique = []
    for j in jobs:
        if j["id"] not in seen:
            seen.add(j["id"])
            unique.append(j)

    payload = {
        "meta": {
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sources": ["join.qq.com", "careers.tencent.com"],
            "total": len(unique),
            "campus_count": sum(1 for j in unique if j["source"] == "campus"),
            "social_count": sum(1 for j in unique if j["source"] == "social"),
        },
        "jobs": unique,
    }

    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已写入 {OUTPUT}，共 {len(unique)} 条岗位")
    return payload


if __name__ == "__main__":
    main()
