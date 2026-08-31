"""
Pengaturan umum pipeline.
Nilai bisa di-override lewat file .env di root proyek.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env jika ada
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

# ── Paths ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / os.getenv("DATABASE_PATH", "data/db.sqlite")
OUTPUT_DIR = PROJECT_ROOT / os.getenv("OUTPUT_DIR", "output")
EXPORTS_DIR = PROJECT_ROOT / "data" / "exports"

# Pastikan direktori ada
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Scraping ──────────────────────────────────────────────────────────
SCRAPE_DELAY_SECONDS = float(os.getenv("SCRAPE_DELAY_SECONDS", "0.5"))
SCRAPE_WINDOW_DAYS = int(os.getenv("SCRAPE_WINDOW_DAYS", "365"))
MAX_RETRIES = 2
RETRY_BACKOFF = 1.5
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "10"))  # Jumlah worker paralel
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))  # Timeout lebih cepat (detik)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]

# ── API Keys (placeholder — isi di .env) ──────────────────────────────
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "antah-scraper:v1.0")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

TWITTER_USERNAME = os.getenv("TWITTER_USERNAME", "")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")
TWITTER_EMAIL = os.getenv("TWITTER_EMAIL", "")

# ── Laporan ───────────────────────────────────────────────────────────
REPORT_LANGUAGE = "id"  # Bahasa Indonesia

# ── Play Store App IDs (aplikasi publik pemerintah) ───────────────────
PLAYSTORE_APP_IDS = {
    "Mobile JKN (BPJS Kesehatan)": "app.bpjs.mobile",
    "JMO (BPJS Ketenagakerjaan)": "id.go.bpjsketenagakerjaan.jmo",
    "SIGNAL (Samsat Digital Nasional)": "id.go.polri.signal",
    "M-Pajak (DJP Kemenkeu)": "id.go.pajak.mpajak",
    "SatuSehat Mobile (Kemenkes)": "id.kemkes.satusehat.mobile",
    "IKD (Identitas Kependudukan Digital)": "gov.dukcapil.mobile_id",
    "PLN Mobile (Layanan Listrik)": "com.icon.pln123",
    "Taspen Mobile (Pensiun/ASN)": "com.taspen.taspenmobile",
}

# ── Logging ───────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
