import requests
from bs4 import BeautifulSoup

def fetch_and_clean_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # GB18030で明示的にデコード（文字化け対策）
        try:
            html_text = response.content.decode('gb18030', errors='replace')
        except Exception:
            html_text = response.content.decode('utf-8', errors='replace')

        # 本文の不要な要素（スクリプト、ナビ等）を除去
        soup = BeautifulSoup(html_text, 'html.parser')
        for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
            tag.decompose()

        lines = [line.strip() for line in soup.get_text(separator='\n').splitlines() if line.strip()]
        return '\n'.join(lines)[:3000] # トークン節約のため最大3000文字程度を抽出

    except Exception as e:
        print(f"[ERROR] 取得失敗 ({url}): {e}")
        return None