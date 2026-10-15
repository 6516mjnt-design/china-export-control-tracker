import os
from datetime import datetime
from src.fetcher import fetch_and_clean_page
from src.ai_analyzer import analyze_to_markdown

def main():
    # 接続テスト用に、確実にアクセスできる公開ニュースサイト等のURLを指定
    # 例としてロイターやその他の安定したWebサイト、または後ほど中国関連の別URLに変更可能
    target_url = "https://example.com"
    
    print(f"1. サイトの取得開始: {target_url}")
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
    else:
        print("[ERROR] テキストの取得に失敗しました。")

if __name__ == "__main__":
    main()