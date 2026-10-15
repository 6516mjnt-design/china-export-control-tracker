import os
import csv
from datetime import datetime

def main():
    os.makedirs("outputs/reports", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    raw_file = "data/raw_news.txt"
    
    # raw_news.txt がない場合のサンプルデータ作成
    if not os.path.exists(raw_file):
        with open(raw_file, "w", encoding="utf-8") as f:
            f.write("2026-10-15 | 中国商務部 輸出管理関連の最新公告 | https://www.mofcom.gov.cn/zwgk/gonggao/index.html\n")
            f.write("2026-10-10 | JETRO 中国における規制動向レポート | https://www.jetro.go.jp/biznews/china/\n")

    news_items = []
    print(f"1. ローカルデータ ({raw_file}) の読み込み開始...")
    
    with open(raw_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                news_items.append({
                    "date": parts[0],
                    "news_title": parts[1],
                    "news_source": "Curated / Official Source",
                    "news_url": parts[2]
                })
    
    if news_items:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # --- 1. CSV形式での保存 ---
        csv_filepath = "outputs/reports/china_export_control_news.csv"
        with open(csv_filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "news_title", "news_source", "news_url"])
            writer.writeheader()
            writer.writerows(news_items)
        print(f"   └ CSV出力完了: {csv_filepath} ({len(news_items)} 件)")

        # --- 2. Markdownレポートの出力 ---
        print("2. Markdownレポートの作成中...")
        summary_lines = "\n".join([
            f"- [{item['date']}] {item['news_title']} (URL: {item['news_url']})"
            for item in news_items
        ])
        
        markdown_report = f"""## ■ 中国輸出管理・経済安全保障 ニュース動向まとめ
- **更新日**: {today}
- **対象件数**: {len(news_items)} 件
- **データソース**: キュレーション入力データ (`data/raw_news.txt`)

### 登録された重要トピック一覧
{summary_lines}
"""
        
        md_filepath = f"outputs/reports/{today}_china_security.md"
        with open(md_filepath, "w", encoding="utf-8") as f:
            f.write(markdown_report)
            
        print(f"3. レポート保存完了: {md_filepath}")
    else:
        print("[WARN] 読み込めるニュースデータがありません。")

if __name__ == "__main__":
    main()