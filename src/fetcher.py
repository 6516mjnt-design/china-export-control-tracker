import requests
from bs4 import BeautifulSoup

def fetch_and_clean_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding or 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for element in soup(["script", "style", "nav", "footer", "header", "iframe"]):
                element.extract()
            
            text = soup.get_text(separator=' ', strip=True)
            # 取得結果が短すぎる場合（WAF等のアクセス制限画面）
            if len(text) > 100:
                return text
            else:
                print(f"[WARN] 取得テキストが短いためブロックされた可能性があります: {url}")
                return None
        else:
            print(f"[WARN] ステータスコード: {response.status_code} ({url})")
            return None
            
    except Exception as e:
        print(f"[ERROR] アクセスエラー ({url}): {e}")
        return None