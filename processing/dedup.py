"""
Deduplication engine — hapus konten duplikat berdasarkan URL, judul, atau hash.
"""

from difflib import SequenceMatcher

from scrapers.base import Article


class Deduplicator:
    """Deduplikasi artikel berkecepatan tinggi O(1) berdasarkan URL, judul, dan hash."""

    def __init__(self, title_similarity_threshold: float = 0.85):
        self.threshold = title_similarity_threshold

    def deduplicate(self, articles: list[Article]) -> list[Article]:
        """
        Hapus duplikat dari list artikel secara instan.
        """
        import re
        seen_urls = set()
        seen_hashes = set()
        seen_normalized_titles = set()
        unique = []

        for article in articles:
            # 1. URL dedup
            if article.url and article.url in seen_urls:
                continue

            # 2. Content hash dedup
            h = article.content_hash
            if h in seen_hashes:
                continue

            # 3. Fast Normalized Title dedup O(1)
            raw_title = (article.title or "").strip().lower()
            # Hapus tanda baca dan spasi berlebih untuk pembanding judul yang bersih
            norm_title = re.sub(r"[^a-z0-9]", "", raw_title)
            if norm_title and norm_title in seen_normalized_titles:
                continue

            # Lolos semua filter
            if article.url:
                seen_urls.add(article.url)
            seen_hashes.add(h)
            if norm_title:
                seen_normalized_titles.add(norm_title)
            unique.append(article)

        removed = len(articles) - len(unique)
        if removed > 0:
            print(f"  Dedup: {removed} duplikat dihapus, {len(unique)} unik")

        return unique
