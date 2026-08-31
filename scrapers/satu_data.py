"""
Satu Data Indonesia (data.go.id) Scraper.

Mengumpulkan katalog dataset dan publikasi data resmi pemerintah
terkait kependudukan dan layanan publik dari portal nasional data.go.id.
"""

from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()

from scrapers.base import BaseScraper, Article


class SatuDataScraper(BaseScraper):
    """Scraper untuk portal Satu Data Indonesia (data.go.id)."""

    BASE_URL = "https://data.go.id"
    SEARCH_URL = "https://data.go.id/dataset"

    def __init__(self):
        super().__init__(source_type="satu_data", delay=1.0)
        # Enable unverified SSL to handle government internal certs
        self.session.verify = False

    def _parse_search_page(self, html: str) -> list[dict]:
        """Parse halaman pencarian dataset data.go.id."""
        soup = BeautifulSoup(html, "lxml")
        results = []
        seen_links = set()

        # Cari semua link dataset
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if "/dataset/" in href:
                if href in seen_links:
                    continue
                seen_links.add(href)

                full_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                raw_text = a.get_text(separator=" ", strip=True)
                
                # Cari card pembungkus untuk konteks tambahan
                parent = a.find_parent(["div", "article", "li"])
                snippet = ""
                if parent:
                    snippet = parent.get_text(separator=" ", strip=True)

                if raw_text and len(raw_text) > 5:
                    results.append({
                        "title": raw_text,
                        "url": full_url,
                        "snippet": snippet or raw_text,
                    })

        return results

    def scrape(
        self,
        keywords: list[str],
        days_back: int = 365,
        max_results: int = 30,
    ) -> list[Article]:
        """Scrape dataset dari Satu Data Indonesia untuk daftar keywords."""
        articles = []
        seen_urls = set()

        for i, keyword in enumerate(keywords, 1):
            self.logger.info(
                f"[{i}/{len(keywords)}] Satu Data Indonesia keyword: '{keyword}'"
            )

            url = f"{self.SEARCH_URL}?q={quote_plus(keyword)}"
            response = self._fetch(url)
            if not response:
                continue

            results = self._parse_search_page(response.text)
            count = 0

            for r in results:
                if count >= max_results:
                    break

                link = r["url"]
                if link in seen_urls:
                    continue
                seen_urls.add(link)

                title = r["title"]
                snippet = r["snippet"]

                body = (
                    f"Sumber Data: Portal Satu Data Indonesia (data.go.id)\n"
                    f"Judul Dataset: {title}\n"
                    f"Deskripsi & Ringkasan:\n{snippet}\n"
                    f"Tautan Dataset: {link}"
                )

                article = Article(
                    title=f"[Satu Data] {title}",
                    body=body,
                    snippet=snippet[:250],
                    url=link,
                    source_type="satu_data",
                    source_name="Satu Data Indonesia",
                    source_category="government_data",
                    extra_data={"keyword": keyword},
                )
                articles.append(article)
                count += 1

            self.logger.info(f"  → {count} dataset ditemukan untuk '{keyword}'")

        self.logger.info(f"Total: {len(articles)} dataset dari Satu Data Indonesia")
        return articles
