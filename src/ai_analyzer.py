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
以下のニュース一覧テキストを分析し、日本の安全保障貿易管理・法務担当者向けの【日本語要約Markdown】を作成してください。

--- ニュース一覧 ---
{chinese_text}
--------------------

以下のフォーマット（Markdown形式）を厳密に守って出力してください：

## ■ 中国輸出管理・経済安全保障 ニュース動向まとめ
- **対象件数**: {len(chinese_text.splitlines())} 件
- **主な注目テーマ**: (例: 告示発表 / 輸出規制強化 / 双方向投資制限 / その他)
- **重要トピック要約**:
  - 要点1
  - 要点2
  - 要点3
- **日本企業への実務上の注記事項**: (サプライチェーン対応や確認手順など)
"""

    client = genai.Client(api_key=api_key)

    # 混雑(503)対策：最大5回まで、待機時間を伸ばしながらリトライ
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt
            )
            return response.text
        except APIError as e:
            wait_time = (attempt + 1) * 5  # 5秒, 10秒, 15秒... と待機時間を増加
            if attempt < max_retries - 1:
                print(f"[WARN] API呼び出し失敗 (試行 {attempt + 1}/{max_retries}): {e}. {wait_time}秒後に再試行します...")
                time.sleep(wait_time)
            else:
                print(f"[ERROR] APIの混雑が解除されませんでした。フォールバックテキストを出力します。")
                return f"## ■ 中国輸出管理 ニュース一覧（自動抽出結果）\n\nAPI混雑のため要約処理をスキップしました。最新の18件のニュース一覧は同梱のCSVファイル (`china_export_control_news.csv`) をご確認ください。\n\n```text\n{chinese_text}\n```"