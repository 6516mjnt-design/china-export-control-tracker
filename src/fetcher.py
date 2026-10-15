import requests
from bs4 import BeautifulSoup

def fetch_and_clean_page(url):
    # ブラウザからのアクセスに見せかけるためのヘッダー
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # 中国語文字化け対策（GB18030対応）
        response.encoding = response.apparent_encoding or 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 不要なスクリプトやスタイルを削除
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()
            
            text = soup.get_text(separator=' ', strip=True)
            return text
        else:
            print(f"[ERROR] ステータスコード: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] 取得失敗 ({url}): {e}")
        return None