import os
from datetime import datetime
from src.fetcher import fetch_and_clean_page
from src.ai_analyzer import analyze_to_markdown

def main():
    # 本番用の巡回先URL（例: 中国商務部 政策指南・政策発表等）
    target_url = "http://www.mofcom.gov.cn/article/zcfb/"
    
    print(f"1. サイトの取得開始: {target_url}")
    text = fetch_and_clean_page(target_url)
    
    if text:
        print("2. LLMによる要約・Markdown出力中...")
        markdown_report = analyze_to_markdown(text)
        
        os.makedirs("outputs/reports", exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = f"outputs/reports/{today}_china_security.md"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_report)
            
        print(f"3. レポート保存完了: {filepath}")
    else:
        print("[ERROR] テキストの取得に失敗しました。")

if __name__ == "__main__":
    main()