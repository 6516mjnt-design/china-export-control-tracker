import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
import re

def fetch_china_news_list(url):
    """
    JETROなどの安定したビジネスニュースページから、個別ニュースと正確な発行日付を抽出する
    """
    # JETROの中国ビジネスニュース等
    target_url = "https://www.jetro.go.jp/biznews/china/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en;q=0.9",
    }
    
    news_items = []
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding or 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # JETROのニュース一覧アイテム（通常記事リンクやリスト）を探索
            for item in soup.find_all(['div', 'li', 'article']):
                a_tag = item.find('a', href=True)
                if not a_tag:
                    continue
                    
                title = a_tag.get_text(strip=True)
                href = a_tag['href']
                
                # 短すぎるものや関係ないリンクを除外
                if len(title) < 8 or "biznews" not in href:
                    continue
                
                full_url = urljoin(target_url, href)
                
                # 要素内から日付 (YYYY.MM.DD または YYYY-MM-DD) を探す
                item_text = item.get_text()
                date_match = re.search(r'20\d{2}[-/.](?:0[1-9]|1[0-2])[-/.](?:0[1-9]|[12]\d|3[01])', item_text)
                
                item_date_str = ""
                if date_match:
                    raw_date = date_match.group(0).replace('.', '-').replace('/', '-')
                    try:
                        dt = datetime.strptime(raw_date, "%Y-%m-%d")
                        if dt >= thirty_days_ago:
                            item_date_str = raw_date
                    except ValueError:
                        pass
                
                # 日付が見つからない場合はスキップ（正確性を担保）
                if not item_date_str:
                    continue
                
                # 重複を防ぎながら追加
                if not any(item['news_url'] == full_url for item in news_items):
                    news_items.append({
                        "date": item_date_str,
                        "news_title": title,
                        "news_source": "JETRO China Business News",
                        "news_url": full_url
                    })
                    
        return news_items
    except Exception as e:
        print(f"[ERROR] 取得失敗: {e}")
        return []