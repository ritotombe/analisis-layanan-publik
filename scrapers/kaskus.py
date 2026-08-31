"""
Kaskus Forum Scraper — user-generated content dari forum terbesar Indonesia.
Scrape thread-thread diskusi yang relevan dengan layanan publik.
"""

from typing import Optional
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, Article


class KaskusScraper(BaseScraper):
    """Scraper untuk forum Kaskus."""

    BASE_URL = "https://www.kaskus.co.id"
    SEARCH_URL = "https://www.kaskus.co.id/search"

    def __init__(self):
        super().__init__(source_type="kaskus", delay=3)  # lebih pelan untuk forum

    def _parse_search_page(self, html: str) -> list[dict]:
        """Parse halaman hasil pencarian Kaskus."""
        soup = BeautifulSoup(html, "lxml")
        results = []

        # Kaskus search results biasanya ada di elemen list
        for item in soup.select("[class*='thread'], [class*='search-result'], article"):
            title_el = item.select_one("a[class*='title'], h2 a, h3 a")
            if not title_el:
                continue

            url = title_el.get("href", "")
            if url and not url.startswith("http"):
                url = self.BASE_URL + url

            date_el = item.select_one(
                "time, [class*='date'], [class*='time'], span.grey"
            )
            snippet_el = item.select_one(
                "[class*='snippet'], [class*='content'], p"
            )

            results.append({
                "title": title_el.get_text(strip=True),
                "url": url,
                "date": date_el.get_text(strip=True) if date_el else "",
                "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
            })

        return results

    def _parse_thread(self, html: str) -> dict:
        """Parse halaman thread Kaskus → original post + replies."""
        soup = BeautifulSoup(html, "lxml")

        # Original post
        op_body = ""
        op_el = soup.select_one(
            "[class*='entry'], [class*='post-body'], .post-content"
        )
        if op_el:
            op_body = op_el.get_text(separator=" ", strip=True)

        # Replies / komentar
        replies = []
        for reply_el in soup.select(
            "[class*='reply'], [class*='comment'], .post-entry"
        ):
            text = reply_el.get_text(separator=" ", strip=True)
            if text and len(text) > 20:
                replies.append(text)

        return {
            "body": op_body,
            "replies": replies[:20],  # max 20 replies
        }

    def scrape(
        self,
        keywords: list[str],
        days_back: int = 365,
        max_results: int = 30,
    ) -> list[Article]:
        """Scrape Kaskus threads untuk keyword yang diberikan."""
        articles = []
        seen_urls = set()

        for i, keyword in enumerate(keywords, 1):
            self.logger.info(
                f"[{i}/{len(keywords)}] Kaskus keyword: '{keyword}'"
            )

            # Search
            search_url = f"{self.SEARCH_URL}?q={quote_plus(keyword)}&order=recent"
            response = self._fetch(search_url)
            if not response:
                continue

            results = self._parse_search_page(response.text)
            count = 0

            for result in results:
                if count >= max_results:
                    break

                url = result.get("url", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                # Fetch thread
                thread_response = self._fetch(url)
                body = ""
                replies_text = ""
                if thread_response:
                    thread_data = self._parse_thread(thread_response.text)
                    body = thread_data.get("body", "")
                    if thread_data.get("replies"):
                        replies_text = "\n---\n".join(thread_data["replies"])

                full_body = body
                if replies_text:
                    full_body += f"\n\n=== KOMENTAR ===\n{replies_text}"

                article = Article(
                    title=result.get("title", ""),
                    body=full_body if full_body else None,
                    snippet=result.get("snippet", ""),
                    url=url,
                    source_type="kaskus",
                    source_name="Kaskus",
                    source_category="user_generated",
                    published_date=result.get("date"),
                    extra_data={"keyword": keyword},
                )
                articles.append(article)
                count += 1

            self.logger.info(f"  → {count} thread dari Kaskus")
            self._rate_limit()

        self.logger.info(f"Total: {len(articles)} thread dari Kaskus")
        return articles
