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
以下の中国政府・メディアのテキストを分析し、日本の安全保障貿易管理・法務担当者向けの【日本語要約Markdown】を作成してください。

--- 中国語本文 ---
{chinese_text}
--------------------

以下のフォーマット（Markdown形式）を厳密に守って出力してください：

## ■ タイトル（日本語訳）
- **文書分類**: (例: 輸出管理公告 / 両用品目規制 / 不確実エンティティリスト / 対外対抗措置 / その他)
- **重要度**: (高 / 中 / 低)
- **タグ**: `#カテゴリ名` `#規制品目` `#商務部`
- **要約**: 
  - 要点1
  - 要点2
  - 要点3
- **主な規制対象**: (品目、HSコード、技術領域、対象企業など)
- **日本企業への実務上の影響**: (サプライチェーン、許可申請対応など)
- **施行日・適用日**: 
"""

    client = genai.Client(api_key=api_key)

    # 混雑(503)対策：最大3回までリトライする処理
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
                print(f"[WARN] API呼び出し失敗 (試行 {attempt + 1}/{max_retries}): {e}. 5秒後に再試行します...")
                time.sleep(5)
            else:
                raise e