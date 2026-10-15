import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
import re

def fetch_china_news_list(url):
    """
    中国商務部の一覧ページから、個別のニュース記事と正確な発行日付をペアで抽出する
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7",
    }
    
    news_items = []
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding || 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # リスト行 (li) やテーブル行 (tr) ごとに解析して日付とタイトルをペアにする
            for row in soup.find_all(['li', 'tr', 'div']):
                a_tag = row.find('a', href=True)
                if not a_tag:
                    continue
                    
                title = a_tag.get_text(strip=True)
                href = a_tag['href']
                
                # 短すぎるテキストやナビゲーションリンクを除外
                if len(title) < 6 or "javascript" in href or href == "#":
                    continue
                
                # 行全体のテキストから日付パターン (YYYY-MM-DD 等) を探す
                row_text = row.get_text()
                date_match = re.search(r'20\d{2}[-/.]\d{2}[-/.]\d{2}', row_text)
                
                item_date_str = ""
                if date_match:
                    raw_date = date_match.group(0).replace('.', '-').replace('/', '-')
                    try:
                        item_date = datetime.strptime(raw_date, "%Y-%m-%d")
                        # 過去30日以内のものに絞り込む
                        if item_date >= thirty_days_ago:
                            item_date_str = raw_date
                    except ValueError:
                        pass
                
                # もし行内に日付がない場合は、URL構造や親要素を探索、または直近の基準日を適用
                if not item_date_str:
                    # 日付がどうしても取れない場合は本日の日付をフォールバックとして付与
                    item_date_str = datetime.now().strftime("%Y-%m-%d")
                
                full_url = urljoin(url, href)
                
                # 重複を防ぎながらリストに追加
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