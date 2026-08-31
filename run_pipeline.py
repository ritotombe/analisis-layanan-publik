#!/usr/bin/env python3
"""
Full pipeline: Scrape → Analyze → Report.

Contoh penggunaan:
    python run_pipeline.py --days 365          # Full pipeline 1 tahun
    python run_pipeline.py --quick             # Google News + Play Store, 7 hari
    python run_pipeline.py --source google_news --category kesehatan
"""

import argparse
import subprocess
import sys

from config.keywords import CATEGORIES


def main():
    parser = argparse.ArgumentParser(
        description="Full pipeline: Scrape → Analyze → Report"
    )
    parser.add_argument(
        "--source", type=str, default="all",
        help="Sumber data (default: all)"
    )
    parser.add_argument(
        "--category", type=str, default=None,
        help=f"Kategori: {', '.join(CATEGORIES.keys())}"
    )
    parser.add_argument(
        "--days", type=int, default=365,
        help="Berapa hari ke belakang (default: 365)"
    )
    parser.add_argument(
        "--max-results", type=int, default=50,
        help="Maks hasil per keyword (default: 50)"
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Mode cepat: Google News + Play Store, 7 hari terakhir"
    )
    args = parser.parse_args()

    # Quick mode override
    if args.quick:
        args.source = "google_news"
        args.days = 7
        args.max_results = 20
        print("⚡ Mode cepat: Google News saja, 7 hari, max 20 per keyword")

    print("=" * 60)
    print("🚀 PIPELINE ANALISIS PAIN POINT LAYANAN PUBLIK")
    print("=" * 60)

    # ── Step 1: Scrape ────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("📥 STEP 1: SCRAPING DATA")
    print("=" * 60)

    scrape_cmd = [
        sys.executable, "run_scrape.py",
        "--source", args.source,
        "--days", str(args.days),
        "--max-results", str(args.max_results),
    ]
    if args.category:
        scrape_cmd.extend(["--category", args.category])

    result = subprocess.run(scrape_cmd, cwd=".")
    if result.returncode != 0:
        print("❌ Scraping gagal!")
        sys.exit(1)

    # ── Step 2: Analyze ───────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("🔬 STEP 2: ANALISIS DATA")
    print("=" * 60)

    analyze_cmd = [sys.executable, "run_analyze.py"]
    if args.category:
        analyze_cmd.extend(["--category", args.category])

    result = subprocess.run(analyze_cmd, cwd=".")
    if result.returncode != 0:
        print("❌ Analisis gagal!")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ PIPELINE SELESAI!")
    print("=" * 60)
    print("\nHasil:")
    print("  📄 Laporan: output/laporan_*.md")
    print("  📊 Charts:  output/chart_*.png")
    print("  📋 CSV:     data/exports/analisis_*.csv")
    print("  🗄️  Database: data/db.sqlite")


if __name__ == "__main__":
    main()
