import os
import time
from google import genai
from google.genai.errors import APIError

def analyze_to_markdown(news_text_summary):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY が設定されていません。")

    prompt = f"""
あなたは中国の経済安全保障・輸出管理・対外法制の専門アナリストです。
以下は直近1か月間に中国商務部（MOFCOM）等で発表された個別ニュース・告示のタイトルと日付の一覧です。
この一覧を分析し、日本の安全保障貿易管理・法務担当者向けの【日本語要約Markdownレポート】を作成してください。

--- ニュース一覧 ---
{news_text_summary}
--------------------

以下のフォーマット（Markdown形式）を厳密に守って出力してください：

## ■ 中国輸出管理・経済安全保障 直近の動向まとめ
- **対象期間**: 過去30日間
- **抽出件数**: {len(news_text_summary.splitlines())} 件
- **主要なトピックの分類**:
  - 分類1（例: 輸出管理・貿易公告）
  - 分類2（例: 投資環境・外資政策）
- **重要トピックの日本語解説・ハイライト**:
  - [日付] タイトルの和訳と実務上のポイント
  - [日付] タイトルの和訳と実務上のポイント
- **日本企業への実務上の影響・推奨アクション**:
"""

    client = genai.Client(api_key=api_key)

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
                return f"## ■ 中国輸出管理 ニュース動向一覧\n\nAPI混雑のため要約をスキップしました。詳細は同梱のCSVファイルをご確認ください。\n\n{news_text_summary}"