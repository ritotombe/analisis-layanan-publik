"""
Base scraper — kelas abstrak yang digunakan semua scraper.
Menyediakan: rate limiting, retry, user-agent rotation, logging, dan interface umum.
"""

import hashlib
import json
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Optional

import requests

from config.settings import (
    SCRAPE_DELAY_SECONDS,
    MAX_RETRIES,
    RETRY_BACKOFF,
    USER_AGENTS,
    LOG_DIR,
)


@dataclass
class Article:
    """Representasi satu konten yang di-scrape."""
    title: str
    body: Optional[str] = None
    snippet: Optional[str] = None
    url: Optional[str] = None
    source_type: str = ""           # google_news, news_site, kaskus, dll
    source_name: Optional[str] = None
    source_category: str = "news"   # 'news' atau 'user_generated'
    author: Optional[str] = None
    published_date: Optional[str] = None
    rating: Optional[int] = None    # untuk Play Store reviews
    extra_data: dict = field(default_factory=dict)

    @property
    def content_hash(self) -> str:
        """Hash konten untuk deduplication."""
        text = f"{self.title or ''}{self.body or ''}"
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    @property
    def full_text(self) -> str:
        """Gabungan title + body untuk analisis."""
        parts = []
        if self.title:
            parts.append(self.title)
        if self.body:
            parts.append(self.body)
        return " ".join(parts)

    def to_dict(self) -> dict:
        """Konversi ke dictionary untuk penyimpanan."""
        d = asdict(self)
        d["content_hash"] = self.content_hash
        d["extra_data"] = json.dumps(d.get("extra_data", {}), ensure_ascii=False)
        return d


class BaseScraper(ABC):
    """Kelas dasar untuk semua scraper."""

    def __init__(self, source_type: str, delay: float = None):
        self.source_type = source_type
        self.delay = delay or SCRAPE_DELAY_SECONDS
        self.session = requests.Session()
        self._setup_logging()

    def _setup_logging(self):
        """Setup logger per scraper."""
        self.logger = logging.getLogger(f"scraper.{self.source_type}")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            # File handler
            fh = logging.FileHandler(
                LOG_DIR / f"scraper_{self.source_type}.log",
                encoding="utf-8",
            )
            fh.setFormatter(logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s"
            ))
            self.logger.addHandler(fh)

            # Console handler
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
            ))
            self.logger.addHandler(ch)

    def _get_headers(self) -> dict:
        """Dapatkan headers dengan User-Agent acak."""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

    def _rate_limit(self):
        """Tunggu sesuai delay + jitter."""
        jitter = random.uniform(0.5, 1.5)
        wait = self.delay * jitter
        time.sleep(wait)

    def _fetch(self, url: str, params: dict = None) -> Optional[requests.Response]:
        """
        Fetch URL dengan retry dan rate limiting.
        Returns None jika gagal setelah semua retry.
        """
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                self._rate_limit()
                response = self.session.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                    timeout=30,
                )
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response else "?"
                self.logger.warning(
                    f"HTTP {status} untuk {url} (percobaan {attempt}/{MAX_RETRIES})"
                )
                if status == 429:
                    # Too Many Requests — tunggu lebih lama
                    wait = RETRY_BACKOFF ** attempt * 5
                    self.logger.info(f"Rate limited, tunggu {wait}s...")
                    time.sleep(wait)
                elif status in (403, 404):
                    # Forbidden atau Not Found — skip
                    self.logger.warning(f"Skip {url}: HTTP {status}")
                    return None
                else:
                    time.sleep(RETRY_BACKOFF ** attempt)
            except requests.exceptions.RequestException as e:
                self.logger.warning(
                    f"Error fetch {url}: {e} (percobaan {attempt}/{MAX_RETRIES})"
                )
                time.sleep(RETRY_BACKOFF ** attempt)

        self.logger.error(f"Gagal fetch {url} setelah {MAX_RETRIES} percobaan")
        return None

    def _cutoff_date(self, days_back: int) -> datetime:
        """Hitung tanggal batas untuk filter waktu."""
        return datetime.now() - timedelta(days=days_back)

    @abstractmethod
    def scrape(
        self,
        keywords: list[str],
        days_back: int = 365,
        max_results: int = 100,
    ) -> list[Article]:
        """
        Scrape data berdasarkan keywords.
        
        Args:
            keywords: Daftar kata kunci pencarian
            days_back: Berapa hari ke belakang
            max_results: Maksimum hasil per keyword
            
        Returns:
            List of Article objects
        """
        ...

    def scrape_category(
        self,
        category: str,
        days_back: int = 365,
        max_results_per_keyword: int = 50,
    ) -> list[Article]:
        """
        Scrape semua keyword dalam satu kategori.
        Convenience method yang menggunakan config/keywords.py.
        """
        from config.keywords import get_keywords_for_category

        keywords = get_keywords_for_category(category)
        self.logger.info(
            f"Scraping kategori '{category}' dengan {len(keywords)} keyword..."
        )
        return self.scrape(keywords, days_back, max_results_per_keyword)

    def scrape_all(
        self,
        days_back: int = 365,
        max_results_per_keyword: int = 50,
    ) -> list[Article]:
        """Scrape semua keyword dari semua kategori."""
        from config.keywords import get_all_keywords

        keywords = get_all_keywords()
        self.logger.info(
            f"Scraping semua {len(keywords)} keyword..."
        )
        return self.scrape(keywords, days_back, max_results_per_keyword)
