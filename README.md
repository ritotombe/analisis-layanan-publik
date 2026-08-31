# 📊 Analisis Pain Point Layanan Publik Indonesia

Pipeline Python untuk scraping dan menganalisis **pain point masyarakat** dalam mengakses layanan publik pemerintah, khususnya akibat **ketidakterpaduan data kependudukan**.

## 🎯 Tujuan

Menjawab 4 pertanyaan riset:
1. **Pain point per kategori** — Apa saja masalah akibat data tidak sinkron?
2. **Layanan yang dihindari** — Layanan mana yang bikin warga "malas menggunakan"?
3. **Bottleneck waktu** — Di mana waktu paling terbuang?
4. **Kelompok terdampak** — Siapa yang paling kena dampak? (lansia, disabilitas, 3T)

## 📂 Kategori Program

| # | Kategori | Sub-isu |
|---|----------|---------|
| 1 | 🏥 Kesehatan | RS berkualitas, Pemeriksaan gratis, TBC, Data RS, Farmasi |
| 2 | 🍚 Pangan | Lumbung pangan, Makan bergizi gratis |
| 3 | 📚 Pendidikan | Sekolah unggul, Sarpras sekolah |
| 4 | 🤝 Kesejahteraan | Bansos adaptif, Kartu usaha, ASN |
| 5 | 🛣️ Infrastruktur | Infrastruktur desa, Perumahan |
| 6 | 💰 Penerimaan Negara | Pajak, PNBP |

## 📡 Sumber Data

| Sumber | Tipe | API Key? |
|--------|------|----------|
| Google News RSS | Berita | ❌ Tidak perlu |
| Kompas, Detik, Tribunnews, Tempo, CNN ID | Berita | ❌ Tidak perlu |
| Kaskus Forum | User-generated | ❌ Tidak perlu |
| YouTube Comments | User-generated | ✅ Opsional (gratis) |
| Google Play Store Reviews | User-generated | ❌ Tidak perlu |
| LAPOR! (lapor.go.id) | User-generated | ❌ Tidak perlu |
| Reddit r/indonesia | User-generated | ✅ Opsional (gratis) |

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup API keys (opsional)

```bash
cp .env.example .env
# Edit .env dan isi API keys yang dipunya
```

### 3. Jalankan pipeline (Pilih Mode)

#### 🌙 Mode Background / Offline (Bisa Tutup Laptop)
Menggunakan `caffeinate` (macOS) dan `nohup` sehingga proses scraping dan analisis tetap berjalan di latar belakang meskipun layar mati atau laptop ditutup:
```bash
./run_background.sh                    # Full pipeline 1 tahun di background
./run_background.sh --days 30          # 30 hari di background
```

**Perintah Pengelolaan Background:**
```bash
python3 check_status.py                # Cek progres data & status proses
tail -f logs/pipeline_background.log   # Pantau live log secara real-time
./stop_background.sh                   # Hentikan proses jika diperlukan
```

#### ⚡ Mode Interaktif Langsung di Terminal
```bash
# Mode cepat multi-threaded (Google News, 7 hari)
python run_pipeline.py --quick

# Full pipeline di terminal aktif
python run_pipeline.py --days 365
```

### 4. Atau jalankan terpisah

```bash
# Scraping saja
python run_scrape.py --source google_news --days 30
python run_scrape.py --source playstore
python run_scrape.py --source lapor --category kesehatan

# Analisis saja (dari data yang sudah di-scrape)
python run_analyze.py
python run_analyze.py --category pangan
```

## 📄 Output

| File | Deskripsi |
|------|-----------|
| `output/laporan_*.md` | Laporan Markdown terstruktur |
| `output/chart_*.png` | Visualisasi chart |
| `data/exports/analisis_*.csv` | Export CSV untuk analisis lanjutan |
| `data/db.sqlite` | Database SQLite dengan semua data |

## 🏗️ Arsitektur

```
antah/
├── config/          # Konfigurasi, keywords, classification rules
├── scrapers/        # 7 scraper (Google News, news sites, Kaskus, YouTube, Play Store, LAPOR!, Reddit)
├── processing/      # Text cleaning, dedup, multi-dimensional classification
├── analysis/        # Sentiment, pain point extraction, demographics, trends
├── reports/         # Report generation (Markdown, CSV, charts)
├── run_scrape.py    # CLI scraping
├── run_analyze.py   # CLI analisis
└── run_pipeline.py  # CLI full pipeline
```

## 🔑 API Keys

Semua API key bersifat opsional. Pipeline bisa jalan tanpa API key menggunakan Google News RSS, news sites, Kaskus, Play Store, dan LAPOR!.

Untuk menambahkan API key, edit file `.env`:

```env
# Reddit (gratis, daftar di https://old.reddit.com/prefs/apps/)
REDDIT_CLIENT_ID=your_id_here
REDDIT_CLIENT_SECRET=your_secret_here

# YouTube Data API v3 (gratis, buat di https://console.cloud.google.com/)
YOUTUBE_API_KEY=your_key_here
```
