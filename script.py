import datetime
import os
import re
import time
import unicodedata
import urllib.parse

from bs4 import BeautifulSoup
import feedparser
import pandas as pd
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "export_control_news.csv")
RETENTION_DAYS = 30
BACKFILL = os.environ.get("BACKFILL", "0") == "1"
SEARCH_WINDOW = "when:30d" if BACKFILL else "when:7d"
REQUEST_INTERVAL_SEC = 0.5
COLUMNS = ["date", "news_title", "news_source", "news_url"]
REQUIRED_COLUMNS = ["date", "news_title", "news_source"]

# CSISを除外し、より直接的な官庁・規制情報のみに絞ったダイレクトフィード設定
DIRECT_FEEDS = [
    {
        "name": "OFAC (Recent Actions)",
        "type": "rss",
        "url": "https://ofac.treasury.gov/recent-actions.xml"
    },
    {
        "name": "JETRO (安全保障貿易管理)",
        "type": "html",
        "url": "https://www.jetro.go.jp/world/security_trade_control/",
        "selector": "a"
    },
    {
        "name": "Federal Register (BIS/Export Controls)",
        "type": "rss",
        "url": "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=industry-and-security-bureau"
    }
]

# 検索キーワード設定（中国特化）
KEYWORDS_EN = [
    "China export control", "MOFCOM export control", "Entity List China",
    "chip export controls China", "rare earth export restriction",
    "gallium germanium export", "China Unreliable Entity List",
    "US China semiconductor restriction", "China economic security"
]
KEYWORDS_JA = [
    "中国 輸出管理", "中国 商務部", "中国 エンティティリスト",
    "中国 半導体規制", "中国 稀土 規制", "ガリウム ゲルマニウム 輸出規制",
    "中国 経済安全保障", "米中 半導体戦争", "不可靠实体清单",
    "中国デュアルユース", "米中 輸出管理"
]

QUERIES = []
for kw in KEYWORDS_JA:
    QUERIES.append((f"JA: {kw}", f"{kw} {SEARCH_WINDOW}", "ja", "JP", "JP:ja"))
for kw in KEYWORDS_EN:
    QUERIES.append((f"US: {kw}", f"{kw} {SEARCH_WINDOW}", "en-US", "US", "US:en"))

# ---------------------------------------------------------------
# 【極限絞り込み】中国関連、または中国特有の経済安保ワードに限定
# ---------------------------------------------------------------
CHINA_CORE_PATTERN = re.compile(
    r"(中国|China|MOFCOM|商務部|不可靠实体|稀土|ガリウム|ゲルマニウム|米中半導体)",
    re.IGNORECASE,
)

# 市場調査・SEO自動生成記事などのノイズを除外
NOISE_PATTERN = re.compile(
    r"(CAGR|年平均成長率|市場予測|市場の成長|市場シェア|詳細分析|世界市場の主要プレイヤー|"
    r"リサーチレポート|市場規模は成長を続け|プロセス液体制御|エッチングガス|圧力センサー|"
    r"ダイシングダイアタッチフィルム|プローブカード|IPコア|ICソケット)",
    re.IGNORECASE,
)

def nfkc(text: str) -> str:
    return unicodedata.normalize("NFKC", text or "")

def clean_title(raw: str) -> str:
    title = nfkc(raw)
    title = re.sub(r"\s+[-–|]\s+[^-–|]+$", "", title)
    title = re.sub(r"\s*[(（][^()（）]+[)）]\s*$", "", title)
    return title.strip()

def normalize_key(title: str) -> str:
    return re.sub(r"[\s\W_]+", "", nfkc(title)).lower()

def is_relevant(entry_title: str, entry_summary: str = "") -> bool:
    text = nfkc(f"{entry_title} {entry_summary}")
    if NOISE_PATTERN.search(text):
        return False
    return bool(CHINA_CORE_PATTERN.search(text))

def fetch_direct_sources():
    rows = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for feed in DIRECT_FEEDS:
        name = feed["name"]
        url = feed["url"]
        try:
            if feed["type"] == "rss":
                parsed = feedparser.parse(url)
                for entry in parsed.entries:
                    title = clean_title(entry.title)
                    link = getattr(entry, "link", "") or ""
                    if title and is_relevant(title, getattr(entry, "summary", "")):
                        if getattr(entry, "published_parsed", None):
                            pub = datetime.datetime(*entry.published_parsed[:6]) + datetime.timedelta(hours=9)
                            date_str = pub.strftime("%Y-%m-%d")
                        else:
                            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
                        rows.append({
                            "date": date_str,
                            "news_title": title,
                            "news_source": name,
                            "news_url": link
                        })
            elif feed["type"] == "html":
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    encoding = resp.apparent_encoding if resp.apparent_encoding else "utf-8"
                    soup = BeautifulSoup(resp.content.decode(encoding, errors="replace"), "html.parser")
                    elements = soup.select(feed["selector"])
                    base_domain = "/".join(url.split("/")[:3])
                    parsed_count = 0
                    for el in elements:
                        title = clean_title(el.get_text())
                        href = el.get("href", "")
                        if not title or len(title) < 5 or not href or not is_relevant(title):
                            continue
                        link = href if href.startswith("http") else (base_domain + href if href.startswith("/") else base_domain + "/" + href)
                        if any(skip in title.lower() for skip in ["home", "menu", "contact", "sitemap", "プライバシー"]):
                            continue
                        rows.append({
                            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                            "news_title": title,
                            "news_source": name,
                            "news_url": link
                        })
                        parsed_count += 1
                        if parsed_count >= 15:
                            break
        except Exception as e:
            print(f"  {name} 取得エラー: {e}")
        time.sleep(REQUEST_INTERVAL_SEC)
    return rows

def fetch_news():
    direct_entries = fetch_direct_sources()
    raw_entries = []
    for name, query, hl, gl, ceid in QUERIES:
        encoded = urllib.parse.quote(query)
        g_url = f"https://news.google.com/rss/search?q={encoded}&hl={hl}&gl={gl}&ceid={ceid}"
        feed = feedparser.parse(g_url)
        raw_entries.extend(feed.entries)
        time.sleep(REQUEST_INTERVAL_SEC)

    rows, seen = [], set()
    for item in direct_entries:
        key = normalize_key(item["news_title"])
        if key and key not in seen:
            seen.add(key)
            rows.append(item)

    for entry in raw_entries:
        title = clean_title(entry.title)
        if not is_relevant(title, getattr(entry, "summary", "")):
            continue
        key = normalize_key(title)
        if not key or key in seen:
            continue
        seen.add(key)

        if getattr(entry, "published_parsed", None):
            pub = datetime.datetime(*entry.published_parsed[:6]) + datetime.timedelta(hours=9)
            date_str = pub.strftime("%Y-%m-%d")
        else:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")

        rows.append({
            "date": date_str,
            "news_title": title,
            "news_source": "Google News",
            "news_url": getattr(entry, "link", "") or "",
        })
    return rows

def load_existing() -> pd.DataFrame:
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame(columns=COLUMNS)
    try:
        df = pd.read_csv(CSV_PATH, dtype=str, encoding="utf-8-sig")
        return df[COLUMNS] if set(REQUIRED_COLUMNS).issubset(df.columns) else pd.DataFrame(columns=COLUMNS)
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def main():
    print("中国特化・CSIS除外の厳選ニュース収集を開始します...")
    new_rows = fetch_news()
    df_new = pd.DataFrame(new_rows, columns=COLUMNS)
    df_old = load_existing()

    df = pd.concat([df_old, df_new], ignore_index=True)
    df["_key"] = df["news_title"].fillna("").map(normalize_key)
    df.drop_duplicates(subset=["date", "_key"], keep="last", inplace=True)
    df.drop(columns=["_key"], inplace=True)

    df["date_dt"] = pd.to_datetime(df["date"], errors="coerce")
    cutoff = datetime.datetime.now() - datetime.timedelta(days=RETENTION_DAYS)
    df = df[df["date_dt"] >= cutoff].drop(columns=["date_dt"])

    df.sort_values(by=["date", "news_source"], ascending=[False, True], inplace=True)
    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"保存しました: {CSV_PATH}（{len(df)} 行）")

if __name__ == "__main__":
    main()