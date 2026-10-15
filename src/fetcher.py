import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
import re

def fetch_china_news_list(url):
    """
    中国商務部などの一覧ページから個別ニュース（タイトル、実際の掲載日付、URL）を正確に抽出する
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7",
    }
    
    news_items = []
    # 過去30日間の境界日
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding or 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # ニュース一覧のリスト要素 (li タグ等) を検索
            for li in soup.find_all(['li', 'tr', 'div']):
                a_tag = li.find('a', href=True)
                if not a_tag:
                    continue
                    
                title = a_tag.get_text(strip=True)
                href = a_tag['href']
                
                # タイトルが短いメニュー要素やナビゲーションを除外
                if len(title) < 6 or "javascript" in href or href == "#" or "index.html" in href:
                    continue
                
                # 要素内のテキストから YYYY-MM-DD 形式の日付パターンを探す
                li_text = li.get_text()
                date_match = re.search(r'20\d{2}[-/.]\d{2}[-/.]\d{2}', li_text)
                
                if date_match:
                    raw_date = date_match.group(0).replace('.', '-').replace('/', '-')
                    try:
                        item_date = datetime.strptime(raw_date, "%Y-%m-%d")
                        # 過去30日以内のニュースのみを対象とする
                        if item_date >= thirty_days_ago:
                            full_url = urljoin(url, href)
                            # 重複追加の防止
                            if not any(item['news_url'] == full_url for item in news_items):
                                news_items.append({
                                    "date": raw_date,
                                    "news_title": title,
                                    "news_source": "MOFCOM (China)",
                                    "news_url": full_url
                                })
                    except ValueError:
                        continue
                        
        return news_items
    except Exception as e:
        print(f"[ERROR] 一覧取得失敗 ({url}): {e}")
        return []