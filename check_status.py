#!/usr/bin/env python3
"""
Cek status data yang sudah terkumpul dan proses background pipeline.
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime

DATABASE_PATH = Path("data/db.sqlite")
PID_FILE = Path("logs/pipeline.pid")
LOG_FILE = Path("logs/pipeline_background.log")

def get_process_status():
    if not PID_FILE.exists():
        return "❌ Tidak aktif"
    
    try:
        pid = int(PID_FILE.read_text().strip())
        import subprocess
        result = subprocess.run(["ps", "-p", str(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return f"🟢 AKTIF (PID: {pid})"
        else:
            return "⚪ Selesai / Berhenti"
    except Exception:
        return "⚪ Status tidak diketahui"

def check_db_stats():
    if not DATABASE_PATH.exists():
        print("ℹ️ Database belum dibuat.")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    total_articles = c.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    total_analyzed = c.execute("SELECT COUNT(*) FROM analysis_results").fetchone()[0]

    print("\n" + "=" * 60)
    print("📊 STATUS DATA DI DATABASE (SQLite)")
    print("=" * 60)
    print(f"📦 Total Data Tersimpan : {total_articles:,} konten")
    print(f"🔬 Total Data Dianalisis: {total_analyzed:,} konten")

    # Group by source
    c.execute("SELECT source_type, COUNT(*) as count FROM articles GROUP BY source_type ORDER BY count DESC")
    sources = c.fetchall()
    if sources:
        print("\n📡 Rincian per Sumber Data:")
        for s in sources:
            print(f"  • {s['source_type']:<15}: {s['count']:,} konten")

    # Group by category
    c.execute("SELECT category, COUNT(*) as count FROM analysis_results GROUP BY category ORDER BY count DESC")
    cats = c.fetchall()
    if cats:
        print("\n📂 Rincian per Kategori Isu:")
        for cat in cats:
            print(f"  • {cat['category']:<20}: {cat['count']:,} hasil analisis")

    # Latest scraping logs
    c.execute("SELECT source_type, keyword, articles_found, articles_new, status, finished_at FROM scrape_logs ORDER BY id DESC LIMIT 5")
    logs = c.fetchall()
    if logs:
        print("\n📋 5 Log Scraping Terakhir:")
        for l in logs:
            status_emoji = "✅" if l["status"] == "completed" else "⏳"
            print(f"  {status_emoji} [{l['source_type']}] {l['keyword']}: +{l['articles_new']} baru ({l['status']})")

    conn.close()

def main():
    print("=" * 60)
    print("🔍 MONITOR STATUS PIPELINE LAYANAN PUBLIK")
    print("=" * 60)
    print(f"🕒 Waktu Sekarang   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⚙️ Status Background: {get_process_status()}")
    
    check_db_stats()

    if LOG_FILE.exists():
        print("\n" + "=" * 60)
        print("📄 5 Baris Terakhir dari Background Log:")
        print("=" * 60)
        lines = LOG_FILE.read_text(encoding="utf-8", errors="ignore").strip().splitlines()
        for line in lines[-5:]:
            print(f"  {line}")

    print("\n" + "=" * 60)
    print("Perintah Bantuan:")
    print("  • Jalankan background : ./run_background.sh")
    print("  • Pantau live log     : tail -f logs/pipeline_background.log")
    print("  • Hentikan proses     : ./stop_background.sh")
    print("=" * 60)

if __name__ == "__main__":
    main()
