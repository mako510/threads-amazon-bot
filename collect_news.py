"""
STEP 1: 話題収集
Google NewsのRSSフィードから、その日の主要ニュース見出しを取得する。
X/Threadsの「公式トレンドAPI」は一般公開されていないため、
ニュース検索ベースで「今話題になっていそうなトピック」を代わりに収集する方式。
"""
import feedparser
import json
import sys
from datetime import datetime, timezone, timedelta

# 収集するRSSフィード一覧（必要に応じて追加・変更してください）
FEEDS = [
    # Googleニュース 主要トピック（日本）
    "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja",
    # Googleニュース ビジネス
    "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ja&gl=JP&ceid=JP:ja",
    # Googleニュース テクノロジー
    "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ja&gl=JP&ceid=JP:ja",
    # Googleニュース エンタメ
    "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=ja&gl=JP&ceid=JP:ja",
]

MAX_ITEMS_PER_FEED = 10


def collect(feeds=None):
    feeds = feeds or FEEDS
    items = []
    for url in feeds:
        try:
            parsed = feedparser.parse(url)
            for entry in parsed.entries[:MAX_ITEMS_PER_FEED]:
                items.append({
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source_feed": url,
                })
        except Exception as e:
            print(f"[WARN] フィード取得失敗: {url} ({e})", file=sys.stderr)

    # タイトルで重複排除
    seen = set()
    deduped = []
    for it in items:
        if it["title"] and it["title"] not in seen:
            seen.add(it["title"])
            deduped.append(it)

    return deduped


def main():
    news = collect()
    result = {
        "collected_at": datetime.now(timezone(timedelta(hours=9))).isoformat(),
        "count": len(news),
        "items": news,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
