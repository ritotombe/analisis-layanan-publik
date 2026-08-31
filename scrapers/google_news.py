"""
Google News RSS Scraper — sumber utama, tanpa API key.

Cara kerja:
1. Bangun URL RSS dari keyword
2. Parse feed dengan feedparser
3. Follow link ke artikel asli
4. Extract teks artikel dengan BeautifulSoup
"""

from datetime import datetime
from typing import Optional
from urllib.parse import quote_plus

import feedparser
from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, Article


class GoogleNewsScraper(BaseScraper):
    """Scraper Google News via RSS feed."""

    RSS_BASE = "https://news.google.com/rss/search"

    def __init__(self):
        super().__init__(source_type="google_news")

    def _build_rss_url(self, keyword: str, days_back: int = 365) -> str:
        """Bangun URL RSS Google News untuk keyword tertentu."""
        # Google News RSS mendukung parameter waktu via query
        # 'when:Xd' untuk X hari terakhir (max ~30 hari via parameter)
        # Untuk > 30 hari, kita filter di sisi klien
        encoded = quote_plus(keyword)
        time_param = f"when:{min(days_back, 365)}d"
        return (
            f"{self.RSS_BASE}?q={encoded}+{time_param}"
            f"&hl=id&gl=ID&ceid=ID:id"
        )

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse tanggal dari RSS feed ke format ISO."""
        if not date_str:
            return None
        try:
            # feedparser biasanya kasih format RFC 2822
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return date_str

    def _extract_article_text(self, url: str) -> Optional[str]:
        """
        Follow link dan extract teks artikel.
        Google News redirect ke situs asli.
        """
        response = self._fetch(url)
        if not response:
            return None

        try:
            soup = BeautifulSoup(response.text, "lxml")

            # Hapus elemen yang tidak perlu
            for tag in soup.find_all(["script", "style", "nav", "header",
                                      "footer", "aside", "iframe", "noscript"]):
                tag.decompose()

            # Coba extract body artikel dari tag umum
            article_body = None

            # Coba beberapa selector umum untuk situs berita Indonesia
            selectors = [
                {"tag": "article"},
                {"tag": "div", "class_": "detail__body-text"},   # detik
                {"tag": "div", "class_": "read__content"},       # kompas
                {"tag": "div", "class_": "content-detail"},      # tribunnews
                {"tag": "div", "class_": "detail-konten"},
                {"tag": "div", "class_": "article-content"},
                {"tag": "div", "class_": "post-content"},
                {"tag": "div", "class_": "entry-content"},
                {"tag": "div", "id": "article-content"},
                {"tag": "div", "class_": "td-post-content"},
            ]

            for sel in selectors:
                tag_name = sel.pop("tag")
                found = soup.find(tag_name, **sel)
                if found:
                    article_body = found
                    break

            if article_body:
                # Ambil semua paragraf
                paragraphs = article_body.find_all("p")
                if paragraphs:
                    text = " ".join(p.get_text(strip=True) for p in paragraphs)
                else:
                    text = article_body.get_text(separator=" ", strip=True)
            else:
                # Fallback: ambil semua <p> tags dari halaman
                paragraphs = soup.find_all("p")
                text = " ".join(
                    p.get_text(strip=True)
                    for p in paragraphs
                    if len(p.get_text(strip=True)) > 40  # filter paragraf pendek
                )

            # Bersihkan whitespace berlebih
            text = " ".join(text.split())
            return text if len(text) > 100 else None

        except Exception as e:
            self.logger.warning(f"Gagal extract teks dari {url}: {e}")
            return None

    def _extract_source_name(self, entry) -> str:
        """Extract nama sumber dari RSS entry."""
        # Google News menyimpan source di <source> tag
        source = getattr(entry, "source", {})
        if isinstance(source, dict):
            return source.get("title", "Unknown")
        # Fallback: coba dari title (biasanya format "Judul - Sumber")
        if " - " in entry.get("title", ""):
            return entry["title"].rsplit(" - ", 1)[-1].strip()
        return "Unknown"

    def scrape(
        self,
        keywords: list[str],
        days_back: int = 365,
        max_results: int = 50,
    ) -> list[Article]:
        """
        Scrape Google News RSS secara paralel dengan multi-threading.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from config.settings import MAX_WORKERS

        articles = []
        seen_urls = set()
        cutoff = self._cutoff_date(days_back)

        for i, keyword in enumerate(keywords, 1):
            self.logger.info(
                f"[{i}/{len(keywords)}] Scraping keyword: '{keyword}'"
            )

            url = self._build_rss_url(keyword, days_back)
            feed = feedparser.parse(url)

            if feed.bozo and not feed.entries:
                self.logger.warning(f"Feed error untuk '{keyword}': {feed.bozo_exception}")
                continue

            entries_to_process = []
            for entry in feed.entries:
                if len(entries_to_process) >= max_results:
                    break

                link = entry.get("link", "")
                if not link or link in seen_urls:
                    continue
                seen_urls.add(link)

                pub_date = self._parse_date(entry.get("published", ""))
                if pub_date:
                    try:
                        pub_dt = datetime.strptime(pub_date, "%Y-%m-%d %H:%M:%S")
                        if pub_dt < cutoff:
                            continue
                    except ValueError:
                        pass

                title = entry.get("title", "").strip()
                if not title:
                    continue

                snippet = ""
                if entry.get("summary"):
                    soup = BeautifulSoup(entry["summary"], "lxml")
                    snippet = soup.get_text(strip=True)

                source_name = self._extract_source_name(entry)

                entries_to_process.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "source_name": source_name,
                    "pub_date": pub_date,
                    "keyword": keyword,
                })

            if not entries_to_process:
                continue

            # Fetch full articles secara paralel
            def fetch_single_article(item):
                body = self._extract_article_text(item["link"])
                return Article(
                    title=item["title"],
                    body=body or item["snippet"],  # Fallback ke snippet jika full text gagal
                    snippet=item["snippet"],
                    url=item["link"],
                    source_type="google_news",
                    source_name=item["source_name"],
                    source_category="news",
                    published_date=item["pub_date"],
                    extra_data={"keyword": item["keyword"]},
                )

            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = [executor.submit(fetch_single_article, item) for item in entries_to_process]
                for future in as_completed(futures):
                    try:
                        article = future.result()
                        if article:
                            articles.append(article)
                    except Exception as e:
                        self.logger.warning(f"Error processing article: {e}")

            self.logger.info(
                f"  → {len(entries_to_process)} artikel selesai untuk '{keyword}'"
            )

        self.logger.info(f"Total: {len(articles)} artikel dari Google News")
        return articles
