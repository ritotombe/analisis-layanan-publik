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
        """Scrape laporan dari LAPOR! secara paralel."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from config.settings import MAX_WORKERS

        articles = []
        seen_urls = set()

        for i, keyword in enumerate(keywords, 1):
            self.logger.info(
                f"[{i}/{len(keywords)}] LAPOR! keyword: '{keyword}'"
            )

            search_urls = [
                f"{self.BASE_URL}/laporan?q={quote_plus(keyword)}",
                f"{self.BASE_URL}/search?keyword={quote_plus(keyword)}",
            ]

            results = []
            for search_url in search_urls:
                response = self._fetch(search_url)
                if not response:
                    continue

                parsed = self._parse_search_page(response.text)
                if parsed:
                    results = parsed
                    break

            if not results:
                continue

            entries_to_fetch = []
            for result in results:
                if len(entries_to_fetch) >= max_results:
                    break

                url = result.get("url", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                entries_to_fetch.append(result)

            def fetch_single_lapor(result):
                url = result.get("url", "")
                report_data = {}
                if url:
                    detail_response = self._fetch(url)
                    if detail_response:
                        report_data = self._parse_report_page(detail_response.text)

                body = report_data.get("body") or result.get("snippet", "")
                return Article(
                    title=result.get("title", f"Laporan: {keyword}"),
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

            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = [executor.submit(fetch_single_lapor, r) for r in entries_to_fetch]
                for f in as_completed(futures):
                    try:
                        art = f.result()
                        if art:
                            articles.append(art)
                    except Exception as e:
                        self.logger.warning(f"Error fetching lapor report: {e}")

            self.logger.info(f"  → {len(entries_to_fetch)} laporan diproses untuk '{keyword}'")

        self.logger.info(f"Total: {len(articles)} laporan dari LAPOR!")
        return articles
