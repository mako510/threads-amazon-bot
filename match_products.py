"""
STEP 3: 商品マッチング
Amazon Product Advertising API (PA-API 5.0) を使い、
話題に関連するキーワードから商品を検索する。

事前準備:
  pip install python-amazon-paapi
  環境変数 AMAZON_ACCESS_KEY / AMAZON_SECRET_KEY / AMAZON_PARTNER_TAG が必要
"""
import json
import os
import sys

from amazon_paapi import AmazonApi

REGION = "JP"
MAX_ITEMS = 3


def get_client():
    access_key = os.environ.get("AMAZON_ACCESS_KEY")
    secret_key = os.environ.get("AMAZON_SECRET_KEY")
    partner_tag = os.environ.get("AMAZON_PARTNER_TAG")

    missing = [name for name, val in [
        ("AMAZON_ACCESS_KEY", access_key),
        ("AMAZON_SECRET_KEY", secret_key),
        ("AMAZON_PARTNER_TAG", partner_tag),
    ] if not val]
    if missing:
        raise RuntimeError(f"環境変数が未設定です: {', '.join(missing)}")

    return AmazonApi(access_key, secret_key, partner_tag, REGION)


def search_products(keywords: list) -> list:
    amazon = get_client()
    all_results = []

    for kw in keywords:
        try:
            search_result = amazon.search_items(keywords=kw, item_count=MAX_ITEMS)
            for item in (search_result.items or []):
                all_results.append({
                    "asin": item.asin,
                    "title": item.item_info.title.display_value if item.item_info and item.item_info.title else "",
                    "url": item.detail_page_url,
                    "price": (
                        item.offers.listings[0].price.display_amount
                        if item.offers and item.offers.listings else None
                    ),
                    "image": (
                        item.images.primary.large.url
                        if item.images and item.images.primary and item.images.primary.large else None
                    ),
                    "matched_keyword": kw,
                })
        except Exception as e:
            print(f"[WARN] '{kw}' の検索に失敗: {e}", file=sys.stderr)

    # ASINで重複排除
    seen = set()
    deduped = []
    for p in all_results:
        if p["asin"] not in seen:
            seen.add(p["asin"])
            deduped.append(p)

    return deduped[:MAX_ITEMS]


def main():
    raw = sys.stdin.read()
    data = json.loads(raw)
    keywords = data.get("related_product_keywords", [])
    if not keywords:
        print(json.dumps({"error": "キーワードがありません"}, ensure_ascii=False))
        sys.exit(1)

    products = search_products(keywords)
    print(json.dumps({"products": products}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
