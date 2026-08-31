"""
Google Play Store Reviews Scraper — user-generated reviews dari aplikasi pemerintah.

Sumber pain point yang sangat spesifik karena user langsung menilai
pengalaman mereka dengan rating + komentar detail.

Menggunakan library google-play-scraper (tidak perlu API key).
"""

from scrapers.base import BaseScraper, Article
from config.settings import PLAYSTORE_APP_IDS


class PlayStoreReviewsScraper(BaseScraper):
    """Scraper reviews Google Play Store untuk aplikasi pemerintah."""

    def __init__(self):
        super().__init__(source_type="playstore", delay=2)

    def _scrape_app_reviews(
        self, app_id: str, app_label: str, count: int = 200
    ) -> list[Article]:
        """Scrape reviews untuk satu aplikasi."""
        try:
            from google_play_scraper import Sort, reviews

            result, _ = reviews(
                app_id,
                lang="id",
                country="id",
                sort=Sort.NEWEST,
                count=count,
            )

            articles = []
            for review in result:
                # Filter: hanya reviews yang punya teks bermakna
                text = review.get("content", "").strip()
                if not text or len(text) < 20:
                    continue

                score = review.get("score", 0)
                username = review.get("userName", "Anonim")

                # Format tanggal
                pub_date = ""
                if review.get("at"):
                    pub_date = review["at"].strftime("%Y-%m-%d %H:%M:%S")

                article = Article(
                    title=f"Review {app_label} ({score}★): {text[:80]}...",
                    body=text,
                    url=f"https://play.google.com/store/apps/details?id={app_id}",
                    source_type="playstore",
                    source_name=f"Play Store - {app_label}",
                    source_category="user_generated",
                    author=username,
                    published_date=pub_date,
                    rating=score,
                    extra_data={
                        "app_id": app_id,
                        "app_label": app_label,
                        "thumbs_up": review.get("thumbsUpCount", 0),
                        "reply": review.get("replyContent", ""),
                    },
                )
                articles.append(article)

            return articles

        except ImportError:
            self.logger.error(
                "Library google-play-scraper belum terinstall. "
                "Jalankan: pip install google-play-scraper"
            )
            return []
        except Exception as e:
            self.logger.error(f"Error scraping {app_id}: {e}")
            return []

    def scrape(
        self,
        keywords: list[str] = None,
        days_back: int = 365,
        max_results: int = 200,
    ) -> list[Article]:
        """
        Scrape reviews dari semua aplikasi pemerintah.
        
        Parameter `keywords` diabaikan untuk scraper ini — kita scrape
        semua app yang terdaftar di config.
        """
        all_articles = []

        for app_label, app_id in PLAYSTORE_APP_IDS.items():
            self.logger.info(f"Scraping Play Store: {app_label} ({app_id})")

            articles = self._scrape_app_reviews(app_id, app_label, max_results)
            all_articles.extend(articles)

            self.logger.info(f"  → {len(articles)} reviews dari {app_label}")
            self._rate_limit()

        # Filter berdasarkan rating (fokus pada keluhan = rating rendah)
        low_rating = [a for a in all_articles if a.rating and a.rating <= 3]
        self.logger.info(
            f"Total: {len(all_articles)} reviews "
            f"({len(low_rating)} dengan rating ≤ 3★)"
        )

        return all_articles
