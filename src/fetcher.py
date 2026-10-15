import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta

def fetch_china_news_list(url):
    """
    中国商務部などの一覧ページから個別ニュース（タイトル、日付、URL）を取得する
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7",
    }
    
    news_items = []
    # 過去1か月の基準日（30日前）
    one_month_ago = datetime.now() - timedelta(days=30)
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding or 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 記事リストの要素を探す（liタグやaタグの並び）
            for a_tag in soup.find_all('a', href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag['href']
                
                # 短すぎるテキストやメニューリンクを除外
                if len(title) < 5 or "javascript" in href or href == "#":
                    continue
                
                full_url = urljoin(url, href)
                
                # 隣接・親要素から日付文字列を探す処理
                parent = a_tag.parent
                date_str = None
                if parent:
                    # YYYY-MM-DD または YYYY/MM/DD 形式を探す
                    import re
                    match = re.search(r'\d{4}[-/.]\d{2}[-/.]\d{2}', parent.get_text())
                    if match:
                        date_str = match.group(0).replace('.', '-').replace('/', '-')
                
                if not date_str:
                    date_str = datetime.now().strftime("%Y-%m-%d")
                
                news_items.append({
                    "date": date_str,
                    "news_title": title,
                    "news_source": "MOFCOM (China)",
                    "news_url": full_url
                })
                
        return news_items
    except Exception as e:
        print(f"[ERROR] 一覧取得失敗 ({url}): {e}")
        return []