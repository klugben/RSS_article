#!/usr/bin/env python3
from __future__ import annotations

import json
import mimetypes
import os
import re
import ssl
import sqlite3
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


BASE_DIR = Path("/root/tencent_rsync_mac/RSS_article")
REPO_DIR = BASE_DIR / "lumen"
DB_PATH = BASE_DIR / "lumen-data" / "feeds.db"
LUMEN_BIN = REPO_DIR / "target" / "release" / "lumen"
OUTPUT_DIR = BASE_DIR / "output"


TOPIC_RULES = [
    (
        "AI与智能体",
        [
            "ai",
            "agent",
            "claude",
            "gemma",
            "glm",
            "模型",
            "多模态",
            "生成式",
            "大模型",
            "机器学习",
            "人工智能",
        ],
    ),
    (
        "开发与Web技术",
        [
            "web app",
            "网页",
            "浏览器",
            "javascript",
            "windows",
            "html",
            "css",
            "开发",
            "程序",
            "应用程序",
            "代码",
        ],
    ),
    (
        "硬件与设备",
        [
            "眼镜",
            "相机",
            "影像",
            "手机",
            "键盘",
            "手表",
            "wear os",
            "fold",
            "flip",
            "x300",
            "oppo",
            "vivo",
            "dlss",
            "硬件",
        ],
    ),
    (
        "影视与娱乐",
        [
            "电影",
            "剧",
            "作品",
            "预告",
            "超级少女",
            "娱乐",
            "愚人节",
            "游戏",
            "巫师",
            "kitkat",
        ],
    ),
    (
        "社区与活动",
        [
            "大会",
            "活动",
            "报名",
            "线下",
            "社区",
            "蜂巢",
            "2050",
        ],
    ),
    (
        "隐私与数字生活",
        [
            "数字遗产",
            "隐私",
            "数据",
            "效率",
            "数字生活",
            "工作流",
        ],
    ),
    (
        "商业与公司史",
        [
            "苹果",
            "apple",
            "微软",
            "google",
            "阿里云",
            "公司",
            "商业",
            "历史",
        ],
    ),
]


def slugify(name: str, limit: int = 80) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|]+", "_", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().strip(".")
    return cleaned[:limit] or "untitled"


def file_slug(name: str, limit: int = 80) -> str:
    cleaned = slugify(name, limit=limit).replace(" ", "_")
    return cleaned or "file"


def infer_topic(title: str, body: str) -> str:
    haystack = f"{title}\n{body}".lower()
    scores: dict[str, int] = {}
    for topic, keywords in TOPIC_RULES:
        score = sum(1 for keyword in keywords if keyword.lower() in haystack)
        if score:
            scores[topic] = score
    if not scores:
        return "未分类"
    return max(scores.items(), key=lambda item: item[1])[0]


def infer_extension(url: str, content_type: str | None) -> str:
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix
    if suffix and len(suffix) <= 10:
        return suffix
    if content_type:
        guessed = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if guessed:
            return guessed
    return ".bin"


def localize_images(markdown_text: str, article_url: str | None, output_path: Path) -> str:
    image_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
    matches = list(image_pattern.finditer(markdown_text))
    if not matches:
        return markdown_text

    asset_dir = output_path.parent / f"{output_path.stem}_assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    seen_urls: dict[str, str] = {}

    def replacer(match: re.Match[str]) -> str:
        alt_text = match.group(1)
        raw_url = match.group(2).strip()
        if raw_url.startswith("data:"):
            return match.group(0)

        absolute_url = urljoin(article_url or "", raw_url)
        if absolute_url in seen_urls:
            return f"![{alt_text}]({seen_urls[absolute_url]})"

        try:
            request = Request(
                absolute_url,
                headers={"User-Agent": "Mozilla/5.0 RSS-article-exporter"},
            )
            try:
                with urlopen(request, timeout=20) as response:
                    content = response.read()
                    content_type = response.headers.get("Content-Type")
            except Exception:
                insecure = ssl._create_unverified_context()
                with urlopen(request, timeout=20, context=insecure) as response:
                    content = response.read()
                    content_type = response.headers.get("Content-Type")
        except Exception:
            return match.group(0)

        ext = infer_extension(absolute_url, content_type)
        parsed = urlparse(absolute_url)
        base_name = Path(parsed.path).stem or "image"
        filename = file_slug(base_name, limit=50)
        target = asset_dir / f"{filename}{ext}"
        counter = 2
        while target.exists():
            target = asset_dir / f"{filename}_{counter}{ext}"
            counter += 1
        target.write_bytes(content)
        relative = target.relative_to(output_path.parent).as_posix()
        seen_urls[absolute_url] = relative
        return f"![{alt_text}]({relative})"

    return image_pattern.sub(replacer, markdown_text)


def fetch_markdown(article_id: int) -> Path:
    cmd = [
        str(LUMEN_BIN),
        "fetch-full-text",
        str(article_id),
        "--markdown",
    ]
    env = {**os.environ, "RSS_DB_PATH": str(DB_PATH)}
    result = subprocess.run(
        cmd,
        cwd=REPO_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    path = payload["result"]["path"]
    return Path(path)


def write_article(topic_dir: Path, article: sqlite3.Row, markdown_text: str) -> Path:
    published_at = article["published_at"] or ""
    date_prefix = ""
    if published_at:
        try:
            date_prefix = datetime.fromisoformat(published_at.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except ValueError:
            date_prefix = published_at[:10]
    filename = slugify(f"{date_prefix} {article['title']}".strip()) + ".md"
    output_path = topic_dir / filename

    header = [
        "---",
        f'title: "{article["title"].replace("\"", "\\\"")}"',
        f'topic: "{topic_dir.name}"',
        f'source: "{article["feed_title"]}"',
        f'url: "{article["url"] or ""}"',
        f'published_at: "{published_at}"',
        f'article_id: {article["id"]}',
        "---",
        "",
    ]
    localized_markdown = localize_images(markdown_text.strip(), article["url"], output_path)
    output_path.write_text("\n".join(header) + localized_markdown + "\n", encoding="utf-8")
    return output_path


def build_index(grouped: dict[str, list[tuple[str, Path]]]) -> None:
    lines = ["# RSS 文章归档", ""]
    for topic in sorted(grouped):
        lines.append(f"## {topic}")
        lines.append("")
        for title, path in grouped[topic]:
            rel_path = path.relative_to(OUTPUT_DIR)
            lines.append(f"- [{title}]({rel_path.as_posix()})")
        lines.append("")
    (OUTPUT_DIR / "index.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def source_dir_name(feed_title: str) -> str:
    return slugify(feed_title, limit=60)


def main() -> None:
    if OUTPUT_DIR.exists():
        for child in OUTPUT_DIR.iterdir():
            if child.is_dir():
                for nested in child.rglob("*"):
                    if nested.is_file():
                        nested.unlink()
                for nested in sorted(child.rglob("*"), reverse=True):
                    if nested.is_dir():
                        nested.rmdir()
                child.rmdir()
            else:
                child.unlink()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT
            a.id,
            a.title,
            a.url,
            a.published_at,
            a.full_content,
            a.content,
            a.summary,
            f.title AS feed_title
        FROM articles a
        JOIN feeds f ON f.id = a.feed_id
        ORDER BY a.published_at DESC, a.id DESC
        """
    ).fetchall()

    grouped: dict[str, list[tuple[str, Path]]] = defaultdict(list)
    for article in rows:
        markdown_path = fetch_markdown(article["id"])
        markdown_text = markdown_path.read_text(encoding="utf-8")
        topic = infer_topic(article["title"], markdown_text)
        topic_dir = OUTPUT_DIR / source_dir_name(article["feed_title"]) / slugify(topic, limit=40)
        topic_dir.mkdir(parents=True, exist_ok=True)
        output_path = write_article(topic_dir, article, markdown_text)
        grouped[f'{article["feed_title"]} / {topic}'].append((article["title"], output_path))

    build_index(grouped)
    print(json.dumps({"ok": True, "output_dir": str(OUTPUT_DIR), "topics": sorted(grouped.keys()), "article_count": len(rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
