"""
Setup database SQLite.
Jalankan sekali untuk membuat schema, atau otomatis dipanggil oleh pipeline.
"""

import sqlite3
from config.settings import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """Buat atau buka koneksi ke database."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def setup_database():
    """Buat semua tabel yang diperlukan."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── Tabel artikel/konten yang di-scrape ────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Identifikasi
            url TEXT UNIQUE,
            content_hash TEXT,
            
            -- Konten
            title TEXT NOT NULL,
            body TEXT,
            snippet TEXT,
            
            -- Metadata sumber
            source_type TEXT NOT NULL,       -- 'google_news', 'news_site', 'kaskus', 'youtube', 'playstore', 'lapor', 'reddit', 'twitter'
            source_name TEXT,                -- 'kompas.com', 'detik.com', 'kaskus', 'youtube', dll
            source_category TEXT,            -- 'news' atau 'user_generated'
            author TEXT,
            
            -- Waktu
            published_date TEXT,
            scraped_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            
            -- Rating (untuk Play Store reviews)
            rating INTEGER,
            
            -- Metadata tambahan (JSON)
            extra_data TEXT
        )
    """)

    # ── Tabel hasil analisis ──────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            
            -- Klasifikasi kategori
            category TEXT,                   -- 'kesehatan', 'pangan', dll
            sub_issue TEXT,                  -- 'rs_berkualitas', 'bansos_adaptif', dll
            
            -- 3 dimensi klasifikasi
            gov_level TEXT,                  -- 'pusat', 'daerah', 'tidak_teridentifikasi'
            area_type TEXT,                  -- '3T', 'umum', 'tidak_teridentifikasi'
            service_type TEXT,               -- 'digital', 'umum', 'tidak_teridentifikasi'
            
            -- Provinsi (jika teridentifikasi)
            province TEXT,
            
            -- Sentiment
            sentiment TEXT,                  -- 'positif', 'netral', 'negatif'
            sentiment_score REAL,            -- -1.0 sampai 1.0
            
            -- Pain points (JSON array)
            pain_points TEXT,                -- '["data_tidak_valid", "bolak_balik_instansi"]'
            
            -- Kelompok demografis (JSON array)
            demographics TEXT,               -- '["lansia", "masyarakat_3t"]'
            
            -- Sinyal abandonment
            has_abandonment_signal INTEGER DEFAULT 0,
            abandonment_signals TEXT,        -- JSON array
            
            -- Bottleneck
            has_bottleneck INTEGER DEFAULT 0,
            bottleneck_patterns TEXT,         -- JSON array
            
            -- Waktu analisis
            analyzed_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            
            FOREIGN KEY (article_id) REFERENCES articles(id)
        )
    """)

    # ── Tabel log scraping ────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scrape_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            keyword TEXT,
            articles_found INTEGER DEFAULT 0,
            articles_new INTEGER DEFAULT 0,
            articles_duplicate INTEGER DEFAULT 0,
            errors INTEGER DEFAULT 0,
            error_messages TEXT,
            started_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            finished_at TEXT,
            status TEXT DEFAULT 'running'    -- 'running', 'completed', 'failed'
        )
    """)

    # ── Indeks untuk query cepat ──────────────────────────────────────
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_date ON articles(published_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_hash ON articles(content_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_category ON analysis_results(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_gov ON analysis_results(gov_level)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_area ON analysis_results(area_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_sentiment ON analysis_results(sentiment)")

    conn.commit()
    conn.close()
    print(f"✅ Database siap: {DATABASE_PATH}")


if __name__ == "__main__":
    setup_database()
