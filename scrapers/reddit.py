"""
Reddit Scraper — opsional, memerlukan API credentials.

Scrape diskusi dari r/indonesia tentang layanan publik.
Jika API key tidak tersedia, scraper ini di-skip.
"""

from scrapers.base import BaseScraper, Article
from config.settings import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT


class RedditScraper(BaseScraper):
    """Scraper Reddit via PRAW (opsional)."""

    def __init__(self):
        super().__init__(source_type="reddit", delay=1)
        self.has_credentials = bool(REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET)
        self.reddit = None

        if self.has_credentials:
            try:
                import praw
                self.reddit = praw.Reddit(
                    client_id=REDDIT_CLIENT_ID,
                    client_secret=REDDIT_CLIENT_SECRET,
                    user_agent=REDDIT_USER_AGENT,
                )
                self.logger.info("Reddit API terhubung ✓")
            except ImportError:
                self.logger.warning(
                    "Library praw belum terinstall. "
                    "Jalankan: pip install praw"
                )
            except Exception as e:
                self.logger.error(f"Gagal koneksi Reddit: {e}")
        else:
            self.logger.info(
                "Reddit API credentials tidak tersedia — scraper di-skip. "
                "Isi REDDIT_CLIENT_ID dan REDDIT_CLIENT_SECRET di .env"
            )

    def scrape(
        self,
        keywords: list[str],
        days_back: int = 365,
        max_results: int = 50,
    ) -> list[Article]:
        """Scrape Reddit r/indonesia."""
        if not self.reddit:
            self.logger.info("Reddit scraper dilewati (tidak ada API key)")
            return []

        articles = []
        seen_ids = set()
        subreddit = self.reddit.subreddit("indonesia")

        for i, keyword in enumerate(keywords, 1):
            self.logger.info(
                f"[{i}/{len(keywords)}] Reddit keyword: '{keyword}'"
            )

            try:
                submissions = subreddit.search(
                    keyword,
                    sort="relevance",
                    time_filter="year",
                    limit=max_results,
                )

                count = 0
                for submission in submissions:
                    if submission.id in seen_ids:
                        continue
                    seen_ids.add(submission.id)

                    # Kumpulkan top-level comments
                    submission.comments.replace_more(limit=0)
                    comments_text = "\n---\n".join(
                        f"[{c.author}] (↑{c.score}): {c.body}"
                        for c in submission.comments[:15]
                        if c.body and len(c.body) > 20
                    )

                    body = submission.selftext or ""
                    if comments_text:
                        body += f"\n\n=== KOMENTAR ===\n{comments_text}"

                    # Konversi timestamp
                    from datetime import datetime
                    pub_date = datetime.fromtimestamp(
                        submission.created_utc
                    ).strftime("%Y-%m-%d %H:%M:%S")

                    article = Article(
                        title=submission.title,
                        body=body if body else None,
                        url=f"https://reddit.com{submission.permalink}",
                        source_type="reddit",
                        source_name="Reddit r/indonesia",
                        source_category="user_generated",
                        author=str(submission.author),
                        published_date=pub_date,
                        extra_data={
                            "keyword": keyword,
                            "score": submission.score,
                            "num_comments": submission.num_comments,
                            "subreddit": "indonesia",
                        },
                    )
                    articles.append(article)
                    count += 1

                self.logger.info(f"  → {count} posts dari Reddit")

            except Exception as e:
                self.logger.error(f"Error searching '{keyword}': {e}")

        self.logger.info(f"Total: {len(articles)} posts dari Reddit")
        return articles
