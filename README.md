# Threads自動投稿ボット（ニュース要約×Amazonアフィリエイト）

毎日自動で「話題のニュース」を収集し、関連するAmazon商品を紹介する投稿を
Threadsに自動投稿するプログラムです。

## 処理の流れ

1. **話題収集**（`collect_news.py`）: GoogleニュースのRSSから見出しを取得
2. **要約・トピック選定**（`summarize.py`）: Claude APIで紹介しやすい話題を1つ選定
3. **商品マッチング**（`match_products.py`）: Amazon PA-APIで関連商品を検索
4. **投稿文生成**（`generate_post.py`）: Claude APIで投稿文を作成（#PR表記込み）
5. **投稿**（`post_threads.py`）: Threads APIで投稿

`scripts/main.py` がこれらを順番に呼び出します。

## セットアップ

### 1. 必要なアカウント・キー

| 項目 | 取得元 |
|---|---|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com/ |
| `AMAZON_ACCESS_KEY` / `AMAZON_SECRET_KEY` / `AMAZON_PARTNER_TAG` | Amazonアソシエイト管理画面 → PA-API |
| `THREADS_ACCESS_TOKEN` / `THREADS_USER_ID` | Meta for Developers（Threads API、長期アクセストークンは60日ごとに更新が必要） |

### 2. ローカルでテスト

```bash
pip install -r requirements.txt
cp .env.example .env   # .envを編集して実際の値を入れる
export $(cat .env | xargs)  # 環境変数として読み込む（Mac/Linuxの場合）

# 投稿はせず内容だけ確認する場合
python scripts/main.py --dry-run

# 実際に投稿する場合
python scripts/main.py
```

### 3. GitHub Actionsで自動化

1. このプロジェクトをGitHubリポジトリにpush
2. リポジトリの `Settings > Secrets and variables > Actions` に、上記の6つの環境変数をSecretsとして登録
3. `.github/workflows/daily.yml` の `cron` の時刻を好きな時間に調整（デフォルトは日本時間06:00）
4. 初回は `Actions` タブから `workflow_dispatch`（手動実行）で動作確認するのがおすすめ

## 重要な注意事項

- **Amazonアソシエイト規約**: 自動生成投稿でも「#PR」等の広告表示が必須です。本プログラムは投稿文に自動で含めますが、内容が規約に沿っているか定期的に人の目で確認してください。
- **Threads APIの利用規約**: 機械的な大量投稿やスパム的な運用はMetaの規約違反になり得ます。1日1〜数回程度の頻度を推奨します。
- **アクセストークンの更新**: Threadsの長期アクセストークンは60日で失効するため、定期的な更新が必要です。
- **PA-APIの利用条件**: 直近180日で3件以上の紹介実績がないとAPIアクセスが停止する仕様のため、継続的な運用実績が必要です。
- 記事の内容は投稿前に一度は人がチェックする運用を強く推奨します（`--dry-run` で内容を確認してから本番投稿に切り替える等）。

## ディレクトリ構成

```
.
├── scripts/
│   ├── collect_news.py     # ①話題収集
│   ├── summarize.py        # ②要約・トピック選定
│   ├── match_products.py   # ③商品マッチング
│   ├── generate_post.py    # ④投稿文生成
│   ├── post_threads.py     # ⑤Threads投稿
│   └── main.py              # 全体オーケストレーター
├── .github/workflows/daily.yml  # 毎日自動実行の設定
├── logs/                    # 実行結果のログ（自動保存）
├── requirements.txt
└── .env.example
```
