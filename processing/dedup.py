"""
Deduplication engine — hapus konten duplikat berdasarkan URL, judul, atau hash.
"""

from difflib import SequenceMatcher

from scrapers.base import Article


class Deduplicator:
    """Deduplikasi artikel berdasarkan URL, judul, atau content hash."""

    def __init__(self, title_similarity_threshold: float = 0.85):
        self.threshold = title_similarity_threshold

    def deduplicate(self, articles: list[Article]) -> list[Article]:
        """
        Hapus duplikat dari list artikel.
        
        Strategi (berurutan):
        1. URL exact match
        2. Content hash match
        3. Title similarity (fuzzy)
        """
        seen_urls = set()
        seen_hashes = set()
        seen_titles = []
        unique = []

        for article in articles:
            # 1. URL dedup
            if article.url and article.url in seen_urls:
                continue

            # 2. Content hash dedup
            h = article.content_hash
            if h in seen_hashes:
                continue

            # 3. Title similarity
            title = (article.title or "").strip().lower()
            if title and self._is_similar_to_existing(title, seen_titles):
                continue

            # Lolos semua filter
            if article.url:
                seen_urls.add(article.url)
            seen_hashes.add(h)
            if title:
                seen_titles.append(title)
            unique.append(article)

        removed = len(articles) - len(unique)
        if removed > 0:
            print(f"  Dedup: {removed} duplikat dihapus, {len(unique)} unik")

        return unique

    def _is_similar_to_existing(self, title: str, existing: list[str]) -> bool:
        """Cek apakah judul mirip dengan yang sudah ada."""
        for existing_title in existing:
            ratio = SequenceMatcher(None, title, existing_title).ratio()
            if ratio >= self.threshold:
                return True
        return False
