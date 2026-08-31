"""
Direct News Sites Scraper — Kompas, Detik, Tribunnews, Tempo, CNN Indonesia.

Masing-masing situs punya struktur HTML berbeda, jadi setiap situs
punya parser sendiri.
"""

from datetime import datetime
from typing import Optional
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, Article


class _SiteParser:
    """Base parser untuk satu situs berita."""

    name: str = ""
    base_url: str = ""
    search_url_template: str = ""

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        raise NotImplementedError

    def parse_search_results(self, soup: BeautifulSoup) -> list[dict]:
        """Parse halaman hasil pencarian → list of {title, url, snippet, date}."""
        raise NotImplementedError

    def parse_article(self, soup: BeautifulSoup) -> Optional[str]:
        """Parse halaman artikel → full text body."""
        raise NotImplementedError


class KompasParser(_SiteParser):
    name = "kompas.com"
    base_url = "https://search.kompas.com"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        encoded = quote_plus(keyword)
        return f"{self.base_url}/search?q={encoded}&page={page}&sort=date"

    def parse_search_results(self, soup: BeautifulSoup) -> list[dict]:
        results = []
        for item in soup.select(".article__list"):
            title_el = item.select_one(".article__title a")
            if not title_el:
                continue
            date_el = item.select_one(".article__date")
            results.append({
                "title": title_el.get_text(strip=True),
                "url": title_el.get("href", ""),
                "date": date_el.get_text(strip=True) if date_el else "",
            })
        return results

    def parse_article(self, soup: BeautifulSoup) -> Optional[str]:
        body = soup.select_one(".read__content")
        if body:
            return " ".join(p.get_text(strip=True) for p in body.find_all("p"))
        return None


class DetikParser(_SiteParser):
    name = "detik.com"
    base_url = "https://www.detik.com"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        encoded = quote_plus(keyword)
        return f"https://www.detik.com/search/searchall?query={encoded}&page={page}&sortby=time"

    def parse_search_results(self, soup: BeautifulSoup) -> list[dict]:
        results = []
        for item in soup.select("article"):
            title_el = item.select_one("h2 a, h3 a, .media__title a")
            if not title_el:
                continue
            date_el = item.select_one(".media__date, .date, span.info span")
            results.append({
                "title": title_el.get_text(strip=True),
                "url": title_el.get("href", ""),
                "date": date_el.get_text(strip=True) if date_el else "",
            })
        return results

    def parse_article(self, soup: BeautifulSoup) -> Optional[str]:
        body = soup.select_one(".detail__body-text, .itp_bodycontent")
        if body:
            return " ".join(p.get_text(strip=True) for p in body.find_all("p"))
        return None


class TribunnewsParser(_SiteParser):
    name = "tribunnews.com"
    base_url = "https://www.tribunnews.com"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        encoded = quote_plus(keyword)
        return f"{self.base_url}/search?q={encoded}&page={page}"

    def parse_search_results(self, soup: BeautifulSoup) -> list[dict]:
        results = []
        for item in soup.select(".article-list, li.ptb15"):
            title_el = item.select_one("h2 a, h3 a, a.f20")
            if not title_el:
                continue
            date_el = item.select_one("time, .grey")
            results.append({
                "title": title_el.get_text(strip=True),
                "url": title_el.get("href", ""),
                "date": date_el.get_text(strip=True) if date_el else "",
            })
        return results

    def parse_article(self, soup: BeautifulSoup) -> Optional[str]:
        body = soup.select_one(".side-article, .txt-article")
        if body:
            return " ".join(p.get_text(strip=True) for p in body.find_all("p"))
        return None


class TempoParser(_SiteParser):
    name = "tempo.co"
    base_url = "https://www.tempo.co"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        encoded = quote_plus(keyword)
        return f"https://www.tempo.co/search?q={encoded}&page={page}"

    def parse_search_results(self, soup: BeautifulSoup) -> list[dict]:
        results = []
        for item in soup.select(".card-box, .text-card"):
            title_el = item.select_one("a")
            if not title_el:
                continue
            date_el = item.select_one(".date, time")
            results.append({
                "title": title_el.get_text(strip=True),
                "url": title_el.get("href", ""),
                "date": date_el.get_text(strip=True) if date_el else "",
            })
        return results

    def parse_article(self, soup: BeautifulSoup) -> Optional[str]:
        body = soup.select_one("#article-content, .detail-konten")
        if body:
            return " ".join(p.get_text(strip=True) for p in body.find_all("p"))
        return None


class CNNIndonesiaParser(_SiteParser):
    name = "cnnindonesia.com"
    base_url = "https://www.cnnindonesia.com"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        encoded = quote_plus(keyword)
        return f"https://www.cnnindonesia.com/search?query={encoded}&page={page}"

    def parse_search_results(self, soup: BeautifulSoup) -> list[dict]:
        results = []
        for item in soup.select("article, .list-content__item"):
            title_el = item.select_one("h2 a, a.media__link")
            if not title_el:
                continue
            date_el = item.select_one("span.date, .media__date")
            results.append({
                "title": title_el.get_text(strip=True),
                "url": title_el.get("href", ""),
                "date": date_el.get_text(strip=True) if date_el else "",
            })
        return results

    def parse_article(self, soup: BeautifulSoup) -> Optional[str]:
        body = soup.select_one("#detailBody, .detail-text")
        if body:
            return " ".join(p.get_text(strip=True) for p in body.find_all("p"))
        return None


# ═══════════════════════════════════════════════════════════════════════

# Semua parser yang tersedia
SITE_PARSERS = [
    KompasParser(),
    DetikParser(),
    TribunnewsParser(),
    TempoParser(),
    CNNIndonesiaParser(),
]


class NewsSiteScraper(BaseScraper):
    """Scraper langsung ke situs berita Indonesia."""

    def __init__(self):
        super().__init__(source_type="news_site")
        self.parsers = SITE_PARSERS

    def _scrape_site(
        self,
        parser: _SiteParser,
        keywords: list[str],
        max_results: int,
    ) -> list[Article]:
        """Scrape satu situs berita untuk semua keyword."""
        articles = []
        seen_urls = set()
        consecutive_failures = 0

        for keyword in keywords:
            if consecutive_failures >= 3:
                self.logger.warning(
                    f"[{parser.name}] Terblokir atau tidak dapat diakses (3x gagal berturut-turut). Melewati situs ini."
                )
                break

            self.logger.info(f"  [{parser.name}] keyword: '{keyword}'")
            count = 0
            page = 1

            url = parser.build_search_url(keyword, page)
            response = self._fetch(url)
            if not response:
                consecutive_failures += 1
                continue
            
            consecutive_failures = 0
            soup = BeautifulSoup(response.text, "lxml")
            results = parser.parse_search_results(soup)

            if not results:
                continue

            for result in results:
                if count >= max_results:
                    break

                article_url = result.get("url", "")
                if not article_url or article_url in seen_urls:
                    continue

                if article_url.startswith("/"):
                    article_url = parser.base_url + article_url

                seen_urls.add(article_url)

                art_response = self._fetch(article_url)
                body = None
                if art_response:
                    art_soup = BeautifulSoup(art_response.text, "lxml")
                    body = parser.parse_article(art_soup)

                article = Article(
                    title=result.get("title", ""),
                    body=body,
                    url=article_url,
                    source_type="news_site",
                    source_name=parser.name,
                    source_category="news",
                    published_date=result.get("date"),
                    extra_data={"keyword": keyword},
                )
                articles.append(article)
                count += 1

            self._rate_limit()
            self.logger.info(f"  [{parser.name}] → {count} artikel untuk '{keyword}'")

        return articles

    def scrape(
        self,
        keywords: list[str],
        days_back: int = 365,
        max_results: int = 20,
    ) -> list[Article]:
        """Scrape semua situs berita untuk keyword yang diberikan."""
        all_articles = []

        for parser in self.parsers:
            self.logger.info(f"Scraping {parser.name}...")
            try:
                articles = self._scrape_site(parser, keywords, max_results)
                all_articles.extend(articles)
                self.logger.info(f"  {parser.name}: {len(articles)} artikel total")
            except Exception as e:
                self.logger.error(f"Error scraping {parser.name}: {e}")

        self.logger.info(f"Total dari semua news sites: {len(all_articles)} artikel")
        return all_articles
