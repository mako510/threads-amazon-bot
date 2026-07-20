"""
STEP 2: 要約 & トピック選定
collect_news.py が集めたニュース一覧を Claude API に渡し、
「Amazon商品と絡めて紹介しやすい話題」を1つ選んで要約させる。
"""
import json
import os
import sys
import anthropic

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """あなたはSNSトレンド分析の専門家です。
渡されたニュース見出しのリストから、Threadsで紹介記事を書くのに適した
話題を1つ選び、以下のJSON形式だけを出力してください（他のテキストは一切含めない）。

選定基準:
- 世間的に関心が高そうな話題
- Amazon商品（家電・書籍・ガジェット・生活用品・美容・食品など）と自然に絡められる話題
- 特定の実在の人物を誹謗中傷したり、政治的に偏った内容にならないもの

出力JSON形式:
{
  "topic_title": "話題の短いタイトル（20文字以内）",
  "topic_summary": "話題の要約（100〜150文字程度）",
  "related_product_keywords": ["Amazon検索に使うキーワード1", "キーワード2", "キーワード3"],
  "source_link": "元記事のURL"
}
"""


def summarize(news_items: list) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("環境変数 ANTHROPIC_API_KEY が設定されていません")

    client = anthropic.Anthropic(api_key=api_key)

    headlines_text = "\n".join(
        f"- {item['title']} ({item['link']})" for item in news_items
    )

    message = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"以下がニュース見出し一覧です。\n\n{headlines_text}"}
        ],
    )

    text = "".join(block.text for block in message.content if block.type == "text")
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    return json.loads(text)


def main():
    raw = sys.stdin.read()
    data = json.loads(raw)
    items = data.get("items", [])
    if not items:
        print(json.dumps({"error": "ニュース項目が空です"}, ensure_ascii=False))
        sys.exit(1)

    result = summarize(items)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
