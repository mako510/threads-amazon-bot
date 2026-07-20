"""
メインオーケストレーター
① 話題収集 → ② 要約・トピック選定 → ③ 商品マッチング → ④ 投稿文生成 → ⑤ Threads投稿
の一連の流れを実行し、結果をlogsに保存する。

実行方法:
  python scripts/main.py            # 実際に投稿する
  python scripts/main.py --dry-run  # 投稿はせず、生成結果を確認するだけ
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from collect_news import collect
from summarize import summarize
from match_products import search_products
from generate_post import generate
from post_threads import post_to_threads

JST = timezone(timedelta(hours=9))


def run(dry_run: bool = False):
    log = {"started_at": datetime.now(JST).isoformat(), "dry_run": dry_run}

    print("[1/5] 話題収集中...")
    news_items = collect()
    log["news_count"] = len(news_items)
    if not news_items:
        raise RuntimeError("ニュースが1件も取得できませんでした")

    print("[2/5] トピック要約中...")
    topic = summarize(news_items)
    log["topic"] = topic

    print("[3/5] Amazon商品検索中...")
    products = search_products(topic.get("related_product_keywords", []))
    log["products"] = products
    if not products:
        raise RuntimeError("紹介できるAmazon商品が見つかりませんでした")

    print("[4/5] 投稿文生成中...")
    post_text = generate(topic, products)
    log["post_text"] = post_text

    if dry_run:
        print("[5/5] dry-runのため投稿はスキップします")
        log["posted"] = False
    else:
        print("[5/5] Threadsに投稿中...")
        result = post_to_threads(post_text)
        log["posted"] = True
        log["threads_result"] = result

    log["finished_at"] = datetime.now(JST).isoformat()

    os.makedirs("logs", exist_ok=True)
    log_filename = f"logs/{datetime.now(JST).strftime('%Y-%m-%d_%H%M%S')}.json"
    with open(log_filename, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    print(f"\n完了。ログ: {log_filename}")
    print("\n--- 投稿文 ---")
    print(post_text)

    return log


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    try:
        run(dry_run=dry_run)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
