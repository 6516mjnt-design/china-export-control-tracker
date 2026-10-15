import os
from datetime import datetime
from src.fetcher import fetch_and_clean_page
from src.ai_analyzer import analyze_to_markdown

def main():
    # 例：中国商務部 政策発表ページ
    target_url = "http://www.mofcom.gov.cn/article/zcfb/"
    
    print("1. 中国語サイトの取得開始...")
    text = fetch_and_clean_page(target_url)
    
    if text:
        print("2. LLMによる要約・Markdown出力中...")
        markdown_report = analyze_to_markdown(text)
        
        # outputs/reports/YYYY-MM-DD.md に保存
        os.makedirs("outputs/reports", exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = f"outputs/reports/{today}_china_security.md"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_report)
            
        print(f"3. レポート保存完了: {filepath}")

if __name__ == "__main__":
    main()