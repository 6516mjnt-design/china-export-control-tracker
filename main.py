import os
from datetime import datetime
from src.fetcher import fetch_and_clean_page
from src.ai_analyzer import analyze_to_markdown

def main():
    # 巡回候補のターゲットURLリスト（商務部、および海外から安定アクセス可能な中国ビジネス・経済情報源）
    target_urls = [
        "https://www.mofcom.gov.cn/zwgk/zcfb/index.html", # 商務部 政策発表
        "https://www.jetro.go.jp/biznews/china/",         # JETRO 中国ビジネスニュース
    ]
    
    scraped_text = None
    used_url = ""

    for url in target_urls:
        print(f"1. サイトの取得試行中: {url}")
        text = fetch_and_clean_page(url)
        if text:
            scraped_text = text
            used_url = url
            print(f"   └ 取得成功! ({len(text)} 文字)")
            break

    if scraped_text:
        print(f"2. LLM (Gemini) による要約・Markdown出力中... (取得元: {used_url})")
        markdown_report = analyze_to_markdown(scraped_text)
        
        os.makedirs("outputs/reports", exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = f"outputs/reports/{today}_china_security.md"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_report)
            
        print(f"3. レポート保存完了: {filepath}")
    else:
        print("[ERROR] すべてのターゲットURLからのデータ取得に失敗しました。")

if __name__ == "__main__":
    main()