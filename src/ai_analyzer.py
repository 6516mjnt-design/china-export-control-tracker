import os

def analyze_to_markdown(news_text_summary):
    # APIの混雑による接続断を完全に回避するため、抽出データに基づいたレポートを直接生成します
    report_content = f"""## ■ 中国輸出管理・経済安全保障 ニュース動向まとめ
- **データソース**: 中国商務部 (MOFCOM) 政策発表・公告一覧
- **詳細データ**: 同梱のCSVファイル (`china_export_control_news.csv`) に最新のニュース一覧および正確な日付・URLが格納されています。

### 抽出された最新の動向一覧
{news_text_summary}
"""
    return report_content