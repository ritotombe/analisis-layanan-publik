#!/usr/bin/env python3
"""
CLI untuk menjalankan analisis pada data yang sudah di-scrape.

Contoh penggunaan:
    python run_analyze.py
    python run_analyze.py --category pangan
"""

import argparse
import json
import sys

from setup_db import get_connection
from processing.cleaner import TextCleaner
from processing.classifier import ArticleClassifier
from analysis.sentiment import SentimentAnalyzer
from analysis.pain_point_extractor import PainPointExtractor
from analysis.demographic_detector import DemographicDetector
from analysis.trend import TrendAnalyzer
from analysis.llm_enhancer import LLMEnhancer
from reports.generator import ReportGenerator
from config.keywords import CATEGORIES


def fetch_articles(conn, category: str = None) -> list[dict]:
    """Ambil artikel dari database."""
    cursor = conn.cursor()

    if category:
        # Cari artikel yang belum dianalisis untuk kategori ini
        cursor.execute("""
            SELECT a.* FROM articles a
            LEFT JOIN analysis_results ar ON a.id = ar.article_id
            WHERE ar.id IS NULL
            ORDER BY a.published_date DESC
        """)
    else:
        cursor.execute("""
            SELECT a.* FROM articles a
            LEFT JOIN analysis_results ar ON a.id = ar.article_id
            WHERE ar.id IS NULL
            ORDER BY a.published_date DESC
        """)

    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def fetch_all_analyzed(conn) -> list[dict]:
    """Ambil semua hasil analisis dari database."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.title, a.url, a.source_type, a.source_name, a.published_date,
               ar.*
        FROM analysis_results ar
        JOIN articles a ON ar.article_id = a.id
        ORDER BY a.published_date DESC
    """)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def save_analysis(conn, article_id: int, result: dict):
    """Simpan hasil analisis ke database."""
    cursor = conn.cursor()

    pain_points_json = json.dumps(
        [pp["type"] for pp in result.get("pain_points_detail", [])],
        ensure_ascii=False,
    )
    demographics_json = json.dumps(
        result.get("demographics_detail", []),
        ensure_ascii=False,
    )
    abandonment_json = json.dumps(
        result.get("abandonment_signals_detail", []),
        ensure_ascii=False,
    )
    bottleneck_json = json.dumps(
        result.get("bottleneck_patterns_detail", []),
        ensure_ascii=False,
    )

    cursor.execute("""
        INSERT INTO analysis_results (
            article_id, category, sub_issue,
            gov_level, area_type, service_type, province,
            sentiment, sentiment_score,
            pain_points, demographics,
            has_abandonment_signal, abandonment_signals,
            has_bottleneck, bottleneck_patterns
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        article_id,
        result.get("category"),
        result.get("sub_issue"),
        result.get("gov_level"),
        result.get("area_type"),
        result.get("service_type"),
        result.get("province"),
        result.get("sentiment"),
        result.get("sentiment_score"),
        pain_points_json,
        demographics_json,
        1 if result.get("has_abandonment_signal") else 0,
        abandonment_json,
        1 if result.get("has_bottleneck") else 0,
        bottleneck_json,
    ))


def main():
    parser = argparse.ArgumentParser(
        description="Analisis data layanan publik Indonesia"
    )
    parser.add_argument(
        "--category", type=str, default=None,
        help=f"Kategori spesifik: {', '.join(CATEGORIES.keys())}"
    )
    parser.add_argument(
        "--report", action="store_true", default=True,
        help="Generate laporan (default: ya)"
    )
    parser.add_argument(
        "--csv", action="store_true", default=True,
        help="Export CSV (default: ya)"
    )
    parser.add_argument(
        "--charts", action="store_true", default=True,
        help="Generate charts (default: ya)"
    )
    parser.add_argument(
        "--use-ai", action="store_true", default=False,
        help="Gunakan AI (Gemini) untuk menyempurnakan analisis data yang sulit"
    )
    args = parser.parse_args()

    conn = get_connection()

    # Inisialisasi komponen
    cleaner = TextCleaner(use_stemmer=False)
    classifier = ArticleClassifier()
    sentiment_analyzer = SentimentAnalyzer()
    pain_point_extractor = PainPointExtractor()
    demographic_detector = DemographicDetector()
    trend_analyzer = TrendAnalyzer()
    report_gen = ReportGenerator()
    llm = LLMEnhancer() if args.use_ai else None

    # Ambil artikel belum dianalisis
    articles = fetch_articles(conn, args.category)

    if not articles:
        print("ℹ️  Tidak ada artikel baru untuk dianalisis.")
        print("   Jalankan 'python run_scrape.py' dulu untuk mengumpulkan data.")

        # Cek apakah sudah ada hasil analisis sebelumnya
        existing = fetch_all_analyzed(conn)
        if existing:
            print(f"\n📊 Ditemukan {len(existing)} hasil analisis sebelumnya.")
            print("   Membuat laporan dari data yang ada...\n")
            articles_for_report = existing
        else:
            conn.close()
            return
    else:
        print(f"📊 Menganalisis {len(articles)} artikel...\n")

        # Proses setiap artikel
        all_pp_results = []
        all_demo_results = []

        for i, article in enumerate(articles, 1):
            if i % 50 == 0 or i == 1:
                print(f"  [{i}/{len(articles)}] Memproses...")

            # Gabungkan teks
            full_text = " ".join(filter(None, [
                article.get("title", ""),
                article.get("body", ""),
                article.get("snippet", ""),
            ]))

            if not full_text.strip():
                continue

            # Clean teks
            cleaned = cleaner.clean_for_analysis(full_text)

            # Klasifikasi
            classification = classifier.classify(cleaned)

            # Sentiment
            sentiment_result = sentiment_analyzer.analyze(cleaned)

            # Pain points
            pp_result = pain_point_extractor.extract(cleaned)
            all_pp_results.append(pp_result)

            # Demographics
            demo_result = demographic_detector.detect(cleaned)
            all_demo_results.append(demo_result)

            # Gabungkan hasil
            analysis = {
                **classification,
                "sentiment": sentiment_result["sentiment"],
                "sentiment_score": sentiment_result["score"],
                "pain_points_detail": pp_result["pain_points"],
                "has_abandonment_signal": pp_result["abandonment"]["detected"],
                "abandonment_signals_detail": pp_result["abandonment"]["signals"],
                "has_bottleneck": pp_result["bottleneck"]["detected"],
                "bottleneck_patterns_detail": pp_result["bottleneck"]["patterns"],
                "demographics_detail": demo_result["group_keys"],
            }

            # LLM Enhancement (jika aktif dan kategori tidak terdeteksi)
            if args.use_ai and llm and llm.enabled:
                if analysis.get("category") == "tidak_teridentifikasi" or not analysis.get("pain_points_detail"):
                    print(f"    🤖 Menggunakan AI untuk artikel: {article.get('title')[:30]}...")
                    ai_result = llm.analyze_text(article.get("title", ""), full_text)
                    if ai_result:
                        # Timpa hasil rule-based dengan hasil AI
                        analysis.update(ai_result)

            # Simpan ke database
            save_analysis(conn, article["id"], analysis)

        conn.commit()
        print(f"\n✅ Analisis selesai: {len(articles)} artikel diproses")

    # ── Generate laporan ──────────────────────────────────────────────
    print("\n📝 Membuat laporan...")

    # Ambil semua hasil analisis
    all_results = fetch_all_analyzed(conn)

    if not all_results:
        print("⚠️  Tidak ada hasil analisis untuk dibuat laporan.")
        conn.close()
        return

    # Parse JSON fields
    for r in all_results:
        try:
            r["pain_points_detail"] = json.loads(r.get("pain_points", "[]"))
        except (json.JSONDecodeError, TypeError):
            r["pain_points_detail"] = []
        try:
            r["demographics_detail"] = json.loads(r.get("demographics", "[]"))
        except (json.JSONDecodeError, TypeError):
            r["demographics_detail"] = []
        try:
            r["abandonment_signals_detail"] = json.loads(
                r.get("abandonment_signals", "[]")
            )
        except (json.JSONDecodeError, TypeError):
            r["abandonment_signals_detail"] = []
        try:
            r["bottleneck_patterns_detail"] = json.loads(
                r.get("bottleneck_patterns", "[]")
            )
        except (json.JSONDecodeError, TypeError):
            r["bottleneck_patterns_detail"] = []

    # Re-run extractors for summary
    all_pp_results_for_summary = []
    all_demo_results_for_summary = []
    for r in all_results:
        all_pp_results_for_summary.append({
            "pain_points": [{"type": t, "name": t, "icon": "", "matches": [], "match_count": 1}
                            for t in r.get("pain_points_detail", [])],
            "abandonment": {
                "detected": bool(r.get("has_abandonment_signal")),
                "signals": r.get("abandonment_signals_detail", []),
            },
            "bottleneck": {
                "detected": bool(r.get("has_bottleneck")),
                "patterns": r.get("bottleneck_patterns_detail", []),
            },
        })
        all_demo_results_for_summary.append({
            "groups": [{"key": k, "name": k, "icon": ""} for k in r.get("demographics_detail", [])],
            "group_keys": r.get("demographics_detail", []),
        })

    pp_summary = pain_point_extractor.get_pain_point_summary(all_pp_results_for_summary)
    demo_summary = demographic_detector.get_demographic_summary(all_demo_results_for_summary)

    # Trend
    trend_data = trend_analyzer.analyze_volume_trend(all_results)

    # Generate report
    report_path = report_gen.generate_full_report(
        articles=all_results,
        analysis_results=all_results,
        pain_point_summary=pp_summary,
        demographic_summary=demo_summary,
        trend_data=trend_data,
    )

    # CSV export
    if args.csv:
        report_gen.export_csv(all_results)

    # Charts
    if args.charts:
        print("\n📊 Membuat chart...")
        report_gen.generate_charts(all_results)

    print(f"\n{'='*60}")
    print(f"✅ Semua selesai!")
    print(f"   📄 Laporan: {report_path}")
    print(f"{'='*60}")

    conn.close()


if __name__ == "__main__":
    main()
