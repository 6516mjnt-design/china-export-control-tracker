import os
import time
from google import genai
from google.genai.errors import APIError

def analyze_to_markdown(chinese_text):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY が設定されていません。")

    prompt = f"""
あなたは中国の経済安全保障・輸出管理・対外法制の専門アナリストです。
以下は直近1か月間に発表された中国政府（商務部等）の個別ニュース・告示のタイトル一覧です。
この一覧を分析し、日本の安全保障貿易管理・法務担当者向けの【日本語要約Markdownレポート】を作成してください。

--- 直近1か月のニュース一覧 ---
{chinese_text}
--------------------

以下のフォーマット（Markdown形式）で出力してください：

## ■ 中国輸出管理・経済安全保障 直近1か月のニュース動向
- **対象データ期間**: 過去30日間
- **抽出件数**: {len(chinese_text.splitlines())} 件
- **主要なトピック・規制動向の分類**:
  - 分類1（例: 輸出許可・告示関連）
  - 分類2（例: 企業支援・通商政策関連）
- **重要ニュースの日本語解説（抜粋・要約）**:
  - [日付] タイトルの和訳と概要・注記事項
  - [日付] タイトルの和訳と概要・注記事項
- **日本企業への実務上の影響・推奨アクション**:
"""

    client = genai.Client(api_key=api_key)

    # リトライ処理で503混雑を回避しつつ解析実行
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt
            )
            return response.text
        except APIError as e:
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                return f"## ■ 中国輸出管理 ニュース動向一覧\n\nAIによる自動要約が失敗したため、抽出された最新のニュース一覧を以下に記載します。詳細は同梱の `china_export_control_news.csv` をご覧ください。\n\n```text\n{chinese_text}\n```"