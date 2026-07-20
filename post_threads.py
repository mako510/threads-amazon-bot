"""
STEP 5: Threads投稿
Threads公式APIを使い、テキスト投稿を行う。
投稿は「コンテナ作成 → 公開」の2段階。

事前準備:
  環境変数 THREADS_ACCESS_TOKEN / THREADS_USER_ID が必要
  （長期アクセストークンは60日ごとに更新が必要）
"""
import json
import os
import sys
import time
import requests

API_BASE = "https://graph.threads.net/v1.0"


def post_to_threads(text: str) -> dict:
    access_token = os.environ.get("THREADS_ACCESS_TOKEN")
    user_id = os.environ.get("THREADS_USER_ID")

    missing = [n for n, v in [("THREADS_ACCESS_TOKEN", access_token), ("THREADS_USER_ID", user_id)] if not v]
    if missing:
        raise RuntimeError(f"環境変数が未設定です: {', '.join(missing)}")

    # 1. メディアコンテナを作成
    create_res = requests.post(
        f"{API_BASE}/{user_id}/threads",
        params={
            "media_type": "TEXT",
            "text": text,
            "access_token": access_token,
        },
    )
    create_res.raise_for_status()
    creation_id = create_res.json()["id"]

    # Threads側の処理待ち（推奨: 数秒待つ）
    time.sleep(5)

    # 2. 公開
    publish_res = requests.post(
        f"{API_BASE}/{user_id}/threads_publish",
        params={
            "creation_id": creation_id,
            "access_token": access_token,
        },
    )
    publish_res.raise_for_status()

    return publish_res.json()


def main():
    raw = sys.stdin.read()
    data = json.loads(raw)
    text = data.get("post_text")
    if not text:
        print(json.dumps({"error": "post_text がありません"}, ensure_ascii=False))
        sys.exit(1)

    result = post_to_threads(text)
    print(json.dumps({"posted": True, "result": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
