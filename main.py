import os
import csv
from datetime import datetime, timedelta
from src.fetcher import fetch_china_news_list
from src.ai_analyzer import analyze_to_markdown

def main():
    # 商務部の政策発表・公告一覧ページ
    target_url = "https://www.mofcom.gov.cn/zwgk/zcfb/index.html"
    
    print(f"1. 個別ニュース一覧の取得開始: {target_url}")
    news_items = fetch_china_news_list(target_url)
    
    if news_items:
        os.makedirs("outputs/reports", exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        
        # --- 1. CSV形式での保存 (例のexport_control_news.csv形式) ---
        csv_filepath = "outputs/reports/china_export_control_news.csv"
        with open(csv_filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "news_title", "news_source", "news_url"])
            writer.writeheader()
            writer.writerows(news_items)
        print(f"   └ CSV出力完了: {csv_filepath} ({len(news_items)} 件)")

        # --- 2. Geminiによる日本語要約Markdown出力 ---
        print("2. LLM (Gemini) によるニュース一覧の分析・整理中...")
        
        # テキスト化してAIに渡す
        news_text_summary = "\n".join([
            f"- [{item['date']}] {item['news_title']} (URL: {item['news_url']})"
            for item in news_items[:30] # 上位30件
        ])
        
        markdown_report = analyze_to_markdown(news_text_summary)
        
        md_filepath = f"outputs/reports/{today}_china_security.md"
        with open(md_filepath, "w", encoding="utf-8") as f:
            f.write(markdown_report)
            
        print(f"3. レポート保存完了: {md_filepath}")
    else:
        print("[ERROR] ニュース一覧の取得に失敗しました。")

if __name__ == "__main__":
    main()