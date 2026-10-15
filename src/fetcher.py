import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
import re

def fetch_china_news_list(url):
    """
    中国商務部の一覧ページから、個別のニュース記事とURL/HTMLから逆引きした正確な発行日付を抽出する
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7",
    }
    
    news_items = []
    thirty_days_ago = datetime.now() - timedelta(days=30)
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding or 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for row in soup.find_all(['li', 'tr', 'div']):
                a_tag = row.find('a', href=True)
                if not a_tag:
                    continue
                    
                title = a_tag.get_text(strip=True)
                href = a_tag['href']
                
                # 短すぎるテキストや不要なリンクを除外
                if len(title) < 6 or "javascript" in href or href == "#":
                    continue
                
                full_url = urljoin(url, href)
                item_date_str = ""
                
                # 1. URL文字列内から日付パターン（例: t20261010_... や 2026-10/10 など）を探す
                url_date_match = re.search(r'20\d{2}[-_/]?([01]\d)[-_/]?([0123]\d)', full_url)
                if url_date_match:
                    year_match = re.search(r'20\d{2}', full_url)
                    if year_match:
                        y = year_match.group(0)
                        m = url_date_match.group(1)
                        d = url_date_match.group(2)
                        parsed_url_date = f"{y}-{m}-{d}"
                        try:
                            dt = datetime.strptime(parsed_url_date, "%Y-%m-%d")
                            if dt >= thirty_days_ago:
                                item_date_str = parsed_url_date
                        except ValueError:
                            pass
                
                # 2. URLから取れなかった場合は、行内のテキストから日付を探す
                if not item_date_str:
                    row_text = row.get_text()
                    date_match = re.search(r'20\d{2}[-/.]\d{2}[-/.]\d{2}', row_text)
                    if date_match:
                        raw_date = date_match.group(0).replace('.', '-').replace('/', '-')
                        try:
                            dt = datetime.strptime(raw_date, "%Y-%m-%d")
                            if dt >= thirty_days_ago:
                                item_date_str = raw_date
                        except ValueError:
                            pass
                
                # 3. それでも取れない場合は本日の日付をフォールバック
                if not item_date_str:
                    item_date_str = today_str
                
                # 重複を防ぎながら追加
                if not any(item['news_url'] == full_url for item in news_items):
                    news_items.append({
                        "date": item_date_str,
                        "news_title": title,
                        "news_source": "MOFCOM (China)",
                        "news_url": full_url
                    })
                    
        return news_items
    except Exception as e:
        print(f"[ERROR] 一覧取得失敗 ({url}): {e}")
        return []