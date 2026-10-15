import os
import csv
from datetime import datetime
from src.fetcher import fetch_china_news_list
from src.ai_analyzer import analyze_to_markdown

def main():
    # 安定稼働するJETROの中国ニュースをソースに指定
    target_url = "https://www.jetro.go.jp/biznews/china/"
    
    print(f"1. JETRO中国ニュース一覧の取得開始...")
    news_items = fetch_china_news_list(target_url)
    
    if news_items:
        os.makedirs("outputs/reports", exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        
        # --- 1. CSV形式での保存 ---
        csv_filepath = "outputs/reports/china_export_control_news.csv"
        with open(csv_filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "news_title", "news_source", "news_url"])
            writer.writeheader()
            writer.writerows(news_items)
        print(f"   └ CSV出力完了: {csv_filepath} ({len(news_items)} 件)")

        # --- 2. AIによるMOFCOM情報源の推論・補完レポート出力 ---
        print("2. ニュース分析およびMOFCOM公式情報源の紐付けレポート作成中...")
        news_text_summary = "\n".join([
            f"- [{item['date']}] {item['news_title']} (URL: {item['news_url']})"
            for item in news_items[:30]
        ])
        
        markdown_report = analyze_to_markdown(news_text_summary)
        
        md_filepath = f"outputs/reports/{today}_china_security.md"
        with open(md_filepath, "w", encoding="utf-8") as f:
            f.write(markdown_report)
            
        print(f"3. レポート保存完了: {md_filepath}")
    else:
        print("[ERROR] ニュースデータの取得に失敗しました。")

if __name__ == "__main__":
    main()