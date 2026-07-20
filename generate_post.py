"""
STEP 4: 投稿文生成
話題の要約 + マッチした商品情報 を元に、Threadsに投稿する文章をClaude APIで生成する。

重要:
- Amazonアソシエイト規約に基づき「#PR」「広告」等の表記を必ず含める
- Threadsの1投稿あたりの文字数上限（500文字）に収める
"""
import json
import os
import sys
import anthropic

MODEL = "claude-sonnet-5"
THREADS_CHAR_LIMIT = 500

SYSTEM_PROMPT = f"""あなたはThreads運用のプロのコピーライターです。
渡された「話題」と「Amazon商品情報」を元に、Threadsに投稿する文章を1つ作成してください。

ルール:
- 全体で{THREADS_CHAR_LIMIT}文字以内（絶対厳守）
- 冒頭で話題（ニュース）に軽く触れ、読者の関心を引く
- そこから自然な流れで商品を紹介する
- 誇大広告・効果効能の断定表現は使わない
- 投稿の最後に必ず「#PR」を含める（アフィリエイトリンクを含む広告である旨の表示）
- 商品リンクを本文に含める
- 絵文字は控えめに1〜3個程度
- 出力は投稿本文のみ。前置きや説明文は一切つけない
"""


def generate(topic: dict, products: list) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("環境変数 ANTHROPIC_API_KEY が設定されていません")

    if not products:
        raise RuntimeError("紹介できる商品がありません")

    client = anthropic.Anthropic(api_key=api_key)

    product = products[0]  # 最も関連度が高い1件を使用
    user_prompt = f"""
【話題】
タイトル: {topic.get('topic_title')}
要約: {topic.get('topic_summary')}

【紹介する商品】
商品名: {product.get('title')}
価格: {product.get('price')}
URL: {product.get('url')}
"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    text = "".join(block.text for block in message.content if block.type == "text").strip()

    if len(text) > THREADS_CHAR_LIMIT:
        text = text[:THREADS_CHAR_LIMIT - 1].rstrip() + "…"

    return text


def main():
    raw = sys.stdin.read()
    data = json.loads(raw)
    topic = data.get("topic", {})
    products = data.get("products", [])

    post_text = generate(topic, products)
    print(json.dumps({"post_text": post_text, "product_used": products[0] if products else None},
                      ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
