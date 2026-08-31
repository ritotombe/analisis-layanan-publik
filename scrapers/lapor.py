"""
LAPOR! Scraper — keluhan warga langsung ke pemerintah via lapor.go.id.

Sumber goldmine karena keluhan terstruktur dengan kategori, instansi, dan lokasi.
"""

from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, Article


class LaporScraper(BaseScraper):
    """Scraper untuk LAPOR! (lapor.go.id)."""

    BASE_URL = "https://www.lapor.go.id"

    def __init__(self):
        super().__init__(source_type="lapor", delay=3)

    def _parse_search_page(self, html: str) -> list[dict]:
        """Parse halaman pencarian LAPOR!"""
        soup = BeautifulSoup(html, "lxml")
        results = []

        # LAPOR! biasanya menampilkan laporan dalam card/list
        for item in soup.select(
            ".laporan-item, .card, article, [class*='report'], .list-group-item"
        ):
            title_el = item.select_one("h3 a, h4 a, a[class*='title'], .title a")
            if not title_el:
                title_el = item.select_one("a")
            if not title_el:
                continue

            url = title_el.get("href", "")
            if url and not url.startswith("http"):
                url = self.BASE_URL + url

            # Extract metadata
            date_el = item.select_one("time, [class*='date'], .text-muted")
            category_el = item.select_one("[class*='category'], [class*='tag'], .badge")
            status_el = item.select_one("[class*='status']")
            location_el = item.select_one("[class*='location'], [class*='lokasi']")
            snippet_el = item.select_one("p, [class*='content'], [class*='description']")

            results.append({
                "title": title_el.get_text(strip=True),
                "url": url,
                "date": date_el.get_text(strip=True) if date_el else "",
                "category": category_el.get_text(strip=True) if category_el else "",
                "status": status_el.get_text(strip=True) if status_el else "",
                "location": location_el.get_text(strip=True) if location_el else "",
                "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
            })

        return results

    def _parse_report_page(self, html: str) -> dict:
        """Parse halaman detail laporan LAPOR!"""
        soup = BeautifulSoup(html, "lxml")

        body = ""
        body_el = soup.select_one(
            "[class*='content'], [class*='body'], .description, article"
        )
        if body_el:
            body = body_el.get_text(separator=" ", strip=True)

        # Extract metadata tambahan
        instansi = ""
        instansi_el = soup.select_one("[class*='instansi'], [class*='agency']")
        if instansi_el:
            instansi = instansi_el.get_text(strip=True)

        response_text = ""
        response_el = soup.select_one("[class*='response'], [class*='tanggapan']")
        if response_el:
            response_text = response_el.get_text(separator=" ", strip=True)

        return {
            "body": body,
            "instansi": instansi,
            "response": response_text,
        }

    def scrape(
        self,
        keywords: list[str],
        days_back: int = 365,
        max_results: int = 50,
    ) -> list[Article]:
        """Scrape laporan dari LAPOR!"""
        articles = []
        seen_urls = set()

        for i, keyword in enumerate(keywords, 1):
            self.logger.info(
                f"[{i}/{len(keywords)}] LAPOR! keyword: '{keyword}'"
            )

            # Coba beberapa format URL pencarian
            search_urls = [
                f"{self.BASE_URL}/laporan?q={quote_plus(keyword)}",
                f"{self.BASE_URL}/search?keyword={quote_plus(keyword)}",
            ]

            for search_url in search_urls:
                response = self._fetch(search_url)
                if not response:
                    continue

                results = self._parse_search_page(response.text)
                if results:
                    break
            else:
                self.logger.warning(f"  Tidak ada hasil untuk '{keyword}'")
                continue

            count = 0
            for result in results:
                if count >= max_results:
                    break

                url = result.get("url", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                # Fetch detail laporan
                detail_response = self._fetch(url)
                report_data = {}
                if detail_response:
                    report_data = self._parse_report_page(detail_response.text)

                body = report_data.get("body", result.get("snippet", ""))

                article = Article(
                    title=result.get("title", ""),
                    body=body,
                    snippet=result.get("snippet", ""),
                    url=url,
                    source_type="lapor",
                    source_name="LAPOR!",
                    source_category="user_generated",
                    published_date=result.get("date"),
                    extra_data={
                        "keyword": keyword,
                        "lapor_category": result.get("category", ""),
                        "status": result.get("status", ""),
                        "location": result.get("location", ""),
                        "instansi": report_data.get("instansi", ""),
                        "government_response": report_data.get("response", ""),
                    },
                )
                articles.append(article)
                count += 1

            self.logger.info(f"  → {count} laporan dari LAPOR!")
            self._rate_limit()

        self.logger.info(f"Total: {len(articles)} laporan dari LAPOR!")
        return articles
