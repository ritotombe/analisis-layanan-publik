#!/usr/bin/env python3
"""
CLI untuk scraping data.

Contoh penggunaan:
    python run_scrape.py --source all --days 365
    python run_scrape.py --source google_news --category kesehatan
    python run_scrape.py --source playstore
    python run_scrape.py --source lapor --days 30
"""

import argparse
import json
import sys
from datetime import datetime

from setup_db import setup_database, get_connection
from config.keywords import get_all_keywords, get_keywords_for_category, CATEGORIES


# ── Registry scraper ──────────────────────────────────────────────────

def get_scraper(source: str):
    """Inisialisasi scraper berdasarkan nama."""
    if source == "google_news":
        from scrapers.google_news import GoogleNewsScraper
        return GoogleNewsScraper()
    elif source == "news_sites":
        from scrapers.news_sites import NewsSiteScraper
        return NewsSiteScraper()
    elif source == "kaskus":
        from scrapers.kaskus import KaskusScraper
        return KaskusScraper()
    elif source == "youtube":
        from scrapers.youtube_comments import YouTubeCommentsScraper
        return YouTubeCommentsScraper()
    elif source == "playstore":
        from scrapers.playstore_reviews import PlayStoreReviewsScraper
        return PlayStoreReviewsScraper()
    elif source == "lapor":
        from scrapers.lapor import LaporScraper
        return LaporScraper()
    elif source == "reddit":
        from scrapers.reddit import RedditScraper
        return RedditScraper()
    else:
        print(f"❌ Sumber tidak dikenal: {source}")
        print(f"   Pilihan: google_news, playstore, lapor, kaskus, youtube, news_sites, reddit")
        sys.exit(1)


# Sumber data aktif: Google News, Play Store Reviews, Portal Berita Langsung, YouTube
ALL_SOURCES = ["google_news", "playstore", "news_sites", "youtube"]


def save_articles(articles, conn):
    """Simpan artikel ke database secara cepat dengan SQLite INSERT OR IGNORE."""
    cursor = conn.cursor()
    new_count = 0
    dup_count = 0

    for article in articles:
        data = article.to_dict()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO articles (
                    url, content_hash, title, body, snippet,
                    source_type, source_name, source_category,
                    author, published_date, rating, extra_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("url"),
                data.get("content_hash"),
                data.get("title"),
                data.get("body"),
                data.get("snippet"),
                data.get("source_type"),
                data.get("source_name"),
                data.get("source_category"),
                data.get("author"),
                data.get("published_date"),
                data.get("rating"),
                data.get("extra_data"),
            ))
            if cursor.rowcount > 0:
                new_count += 1
            else:
                dup_count += 1
        except Exception:
            dup_count += 1

    conn.commit()
    return new_count, dup_count


def main():
    parser = argparse.ArgumentParser(
        description="Scraping data layanan publik Indonesia"
    )
    parser.add_argument(
        "--source", type=str, default="all",
        help="Sumber data: all, google_news, news_sites, kaskus, youtube, playstore, lapor, reddit"
    )
    parser.add_argument(
        "--category", type=str, default=None,
        help=f"Kategori spesifik: {', '.join(CATEGORIES.keys())}"
    )
    parser.add_argument(
        "--days", type=int, default=365,
        help="Berapa hari ke belakang (default: 365)"
    )
    parser.add_argument(
        "--max-results", type=int, default=50,
        help="Maks hasil per keyword (default: 50)"
    )
    args = parser.parse_args()

    # Setup database
    setup_database()
    conn = get_connection()

    # Tentukan keywords
    if args.category:
        keywords = get_keywords_for_category(args.category)
        print(f"📂 Kategori: {args.category} ({len(keywords)} keywords)")
    else:
        keywords = get_all_keywords()
        print(f"📂 Semua kategori ({len(keywords)} keywords)")

    # Tentukan sumber
    sources = ALL_SOURCES if args.source == "all" else [args.source]

    print(f"🔍 Sumber: {', '.join(sources)}")
    print(f"📅 Periode: {args.days} hari terakhir")
    print(f"📊 Maks per keyword: {args.max_results}")
    print("=" * 60)

    total_new = 0
    total_dup = 0

    for source in sources:
        print(f"\n{'='*60}")
        print(f"▶ Memulai scraping: {source}")
        print(f"{'='*60}")

        try:
            scraper = get_scraper(source)

            # Log mulai
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scrape_logs (source_type, keyword, status)
                VALUES (?, ?, 'running')
            """, (source, f"{len(keywords)} keywords"))
            log_id = cursor.lastrowid
            conn.commit()

            # Scrape
            articles = scraper.scrape(
                keywords=keywords,
                days_back=args.days,
                max_results=args.max_results,
            )

            # Simpan langsung ke database (dedup ditangani instan oleh SQLite)
            new, dup = save_articles(articles, conn)
            total_new += new
            total_dup += dup

            # Update log
            cursor.execute("""
                UPDATE scrape_logs 
                SET articles_found = ?, articles_new = ?, articles_duplicate = ?,
                    finished_at = datetime('now', 'localtime'), status = 'completed'
                WHERE id = ?
            """, (len(articles), new, dup, log_id))
            conn.commit()

            print(f"✅ {source}: {new} baru, {dup} duplikat")

        except Exception as e:
            print(f"❌ Error scraping {source}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"📊 TOTAL: {total_new} artikel baru, {total_dup} duplikat")
    print(f"{'='*60}")

    conn.close()


if __name__ == "__main__":
    main()
