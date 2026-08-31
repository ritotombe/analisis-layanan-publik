"""
Report Generator — menghasilkan laporan dalam Bahasa Indonesia.

Output:
1. Laporan Markdown terstruktur per 4 pertanyaan riset
2. CSV exports per kategori
3. Charts (matplotlib)
"""

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from config.settings import OUTPUT_DIR, EXPORTS_DIR
from config.keywords import CATEGORIES


class ReportGenerator:
    """Generator laporan dalam Bahasa Indonesia."""

    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.exports_dir = EXPORTS_DIR

    def generate_full_report(
        self,
        articles: list[dict],
        analysis_results: list[dict],
        pain_point_summary: dict,
        demographic_summary: dict,
        trend_data: dict = None,
    ) -> str:
        """
        Generate laporan lengkap Markdown.
        
        Returns:
            Path ke file laporan
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"laporan_{timestamp}.md"

        lines = []
        lines.append("# 📊 Laporan Analisis Pain Point Layanan Publik Indonesia")
        lines.append(f"\n**Tanggal Laporan:** {datetime.now().strftime('%d %B %Y, %H:%M WIB')}")
        lines.append(f"\n**Total Data Dianalisis:** {len(articles)} konten")
        lines.append(f"\n**Sumber:** {self._count_sources(articles)}")
        lines.append("\n---\n")

        # === Bagian A ===
        lines.append("## A. Pain Point per Kategori (Akibat Ketidakterpaduan Data)")
        lines.append("")
        lines.append(self._section_a(articles, analysis_results, pain_point_summary))

        # === Bagian B ===
        lines.append("\n## B. Layanan Publik yang \"Malas Digunakan\" Warga")
        lines.append("")
        lines.append(self._section_b(analysis_results))

        # === Bagian C ===
        lines.append("\n## C. Titik Waktu Paling Terbuang (Bottleneck)")
        lines.append("")
        lines.append(self._section_c(pain_point_summary))

        # === Bagian D ===
        lines.append("\n## D. Kelompok Warga Paling Terdampak")
        lines.append("")
        lines.append(self._section_d(demographic_summary, analysis_results))

        # === Bagian E ===
        lines.append("\n## E. Perbandingan Pusat vs Daerah")
        lines.append("")
        lines.append(self._section_e(analysis_results))

        # === Bagian F ===
        lines.append("\n## F. Perbandingan 3T vs Umum")
        lines.append("")
        lines.append(self._section_f(analysis_results))

        # === Bagian G ===
        if trend_data:
            lines.append("\n## G. Analisis Tren")
            lines.append("")
            lines.append(self._section_g(trend_data))

        # === Ringkasan ===
        lines.append("\n---\n")
        lines.append("## 📝 Ringkasan Temuan Utama")
        lines.append("")
        lines.append(self._summary(pain_point_summary, demographic_summary, analysis_results))

        report_content = "\n".join(lines)
        report_path.write_text(report_content, encoding="utf-8")
        print(f"✅ Laporan disimpan: {report_path}")
        return str(report_path)

    def _count_sources(self, articles: list[dict]) -> str:
        """Hitung distribusi sumber."""
        counts = defaultdict(int)
        for a in articles:
            counts[a.get("source_type", "lainnya")] += 1
        parts = [f"{name}: {count}" for name, count in sorted(counts.items())]
        return ", ".join(parts)

    def _section_a(self, articles, analysis_results, pp_summary) -> str:
        """Bagian A: Pain point per kategori."""
        lines = []

        for cat_key, cat_data in CATEGORIES.items():
            icon = cat_data["icon"]
            name = cat_data["name"]

            # Filter analisis untuk kategori ini
            cat_results = [
                r for r in analysis_results
                if r.get("category") == cat_key
            ]

            if not cat_results:
                lines.append(f"### {icon} {name}")
                lines.append("_Belum ada data untuk kategori ini._\n")
                continue

            lines.append(f"### {icon} {name} ({len(cat_results)} konten)")
            lines.append("")

            # Pain points di kategori ini
            cat_pain_points = defaultdict(int)
            for r in cat_results:
                for pp in r.get("pain_points_detail", []):
                    cat_pain_points[pp.get("name", "")] += 1

            if cat_pain_points:
                lines.append("| Pain Point | Jumlah Mentions |")
                lines.append("|------------|-----------------|")
                for pp_name, count in sorted(
                    cat_pain_points.items(), key=lambda x: x[1], reverse=True
                ):
                    lines.append(f"| {pp_name} | {count} |")
                lines.append("")

            # Sub-isu
            sub_counts = defaultdict(int)
            for r in cat_results:
                sub = r.get("sub_issue", "")
                if sub and sub != "tidak_teridentifikasi":
                    sub_counts[sub] += 1

            if sub_counts:
                lines.append("**Sub-isu yang paling banyak dibahas:**")
                for sub_key, count in sorted(
                    sub_counts.items(), key=lambda x: x[1], reverse=True
                ):
                    # Cari nama sub-isu
                    sub_name = sub_key
                    for sub_data in cat_data["sub_issues"].values():
                        if sub_key in cat_data["sub_issues"]:
                            sub_name = cat_data["sub_issues"][sub_key]["name"]
                            break
                    lines.append(f"- {sub_name}: {count} konten")
                lines.append("")

        return "\n".join(lines)

    def _section_b(self, analysis_results) -> str:
        """Bagian B: Layanan yang malas digunakan."""
        lines = []

        # Filter yang punya sinyal abandonment
        abandoned = [
            r for r in analysis_results
            if r.get("has_abandonment_signal")
        ]

        if not abandoned:
            lines.append("_Belum cukup data untuk analisis ini._")
            return "\n".join(lines)

        lines.append(f"**{len(abandoned)}** dari {len(analysis_results)} konten "
                      f"mengandung sinyal warga enggan/malas menggunakan layanan.\n")

        # Group by category
        cat_counts = defaultdict(int)
        for r in abandoned:
            cat_counts[r.get("category", "lainnya")] += 1

        lines.append("| Ranking | Kategori | Jumlah Sinyal Abandonment |")
        lines.append("|---------|----------|--------------------------|")
        for i, (cat, count) in enumerate(
            sorted(cat_counts.items(), key=lambda x: x[1], reverse=True), 1
        ):
            cat_name = CATEGORIES.get(cat, {}).get("name", cat)
            lines.append(f"| {i} | {cat_name} | {count} |")

        # Top sinyal
        signal_counts = defaultdict(int)
        for r in abandoned:
            for sig in r.get("abandonment_signals_detail", []):
                signal_counts[sig] += 1

        if signal_counts:
            lines.append("\n**Sinyal abandonment paling sering:**")
            for sig, count in sorted(
                signal_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]:
                lines.append(f"- \"{sig}\": {count} kali")

        return "\n".join(lines)

    def _section_c(self, pp_summary) -> str:
        """Bagian C: Bottleneck / waktu terbuang."""
        lines = []

        top_bottlenecks = pp_summary.get("top_bottleneck_patterns", [])
        total_bn = pp_summary.get("total_with_bottleneck", 0)

        if not top_bottlenecks:
            lines.append("_Belum cukup data untuk analisis bottleneck._")
            return "\n".join(lines)

        lines.append(f"**{total_bn}** konten mengandung indikasi waktu terbuang.\n")
        lines.append("| Ranking | Pola Bottleneck | Frekuensi |")
        lines.append("|---------|-----------------|-----------|")
        for i, (pattern, count) in enumerate(top_bottlenecks[:10], 1):
            lines.append(f"| {i} | \"{pattern}\" | {count} |")

        # Pain points terkait bottleneck
        top_pps = pp_summary.get("top_pain_points", [])
        if top_pps:
            lines.append("\n**Tipe pain point utama:**")
            for pp_key, pp_data in top_pps[:6]:
                lines.append(
                    f"- {pp_data['icon']} {pp_data['name']}: "
                    f"{pp_data['count']} konten"
                )

        return "\n".join(lines)

    def _section_d(self, demo_summary, analysis_results) -> str:
        """Bagian D: Kelompok warga terdampak."""
        lines = []

        ranking = demo_summary.get("ranking", [])
        total_with = demo_summary.get("total_with_demographics", 0)

        if not ranking:
            lines.append("_Belum cukup data untuk analisis demografis._")
            return "\n".join(lines)

        lines.append(
            f"**{total_with}** konten menyebut kelompok warga spesifik.\n"
        )

        # Tabel ranking
        lines.append("| Ranking | Kelompok | Jumlah Mentions |")
        lines.append("|---------|----------|-----------------|")
        for i, (key, data) in enumerate(ranking, 1):
            lines.append(f"| {i} | {data['icon']} {data['name']} | {data['count']} |")

        # Matriks kelompok × kategori
        lines.append("\n**Matriks Kelompok × Kategori:**\n")

        # Header
        cat_names = [CATEGORIES[k]["name"] for k in CATEGORIES if k in CATEGORIES]
        header = "| Kelompok | " + " | ".join(cat_names) + " |"
        sep = "|----------|" + "|".join(["----" for _ in cat_names]) + "|"
        lines.append(header)
        lines.append(sep)

        # Data per kelompok
        for key, data in ranking:
            cat_counts = defaultdict(int)
            for r in analysis_results:
                if key in r.get("demographics_detail", []):
                    cat_counts[r.get("category", "")] += 1

            row_values = [str(cat_counts.get(k, 0)) for k in CATEGORIES]
            lines.append(f"| {data['icon']} {data['name']} | " + " | ".join(row_values) + " |")

        return "\n".join(lines)

    def _section_e(self, analysis_results) -> str:
        """Bagian E: Pusat vs Daerah."""
        lines = []

        pusat = [r for r in analysis_results if r.get("gov_level") == "pusat"]
        daerah = [r for r in analysis_results if r.get("gov_level") == "daerah"]

        lines.append(f"- **Pusat:** {len(pusat)} konten")
        lines.append(f"- **Daerah:** {len(daerah)} konten\n")

        if pusat or daerah:
            lines.append("| Metrik | Pusat | Daerah |")
            lines.append("|--------|-------|--------|")

            # Sentiment rata-rata
            pusat_sent = [r.get("sentiment_score", 0) for r in pusat]
            daerah_sent = [r.get("sentiment_score", 0) for r in daerah]
            avg_p = round(sum(pusat_sent) / len(pusat_sent), 3) if pusat_sent else 0
            avg_d = round(sum(daerah_sent) / len(daerah_sent), 3) if daerah_sent else 0
            lines.append(f"| Sentimen rata-rata | {avg_p} | {avg_d} |")

            # Pain point count
            pp_p = sum(1 for r in pusat if r.get("pain_points_detail"))
            pp_d = sum(1 for r in daerah if r.get("pain_points_detail"))
            lines.append(f"| Konten dengan pain point | {pp_p} | {pp_d} |")

            # Abandonment
            ab_p = sum(1 for r in pusat if r.get("has_abandonment_signal"))
            ab_d = sum(1 for r in daerah if r.get("has_abandonment_signal"))
            lines.append(f"| Sinyal abandonment | {ab_p} | {ab_d} |")

        return "\n".join(lines)

    def _section_f(self, analysis_results) -> str:
        """Bagian F: 3T vs Umum."""
        lines = []

        t3 = [r for r in analysis_results if r.get("area_type") == "3T"]
        umum = [r for r in analysis_results if r.get("area_type") == "umum"]

        lines.append(f"- **Daerah 3T:** {len(t3)} konten")
        lines.append(f"- **Daerah Umum:** {len(umum)} konten\n")

        if t3 or umum:
            lines.append("| Metrik | 3T | Umum |")
            lines.append("|--------|-----|------|")

            t3_sent = [r.get("sentiment_score", 0) for r in t3]
            umum_sent = [r.get("sentiment_score", 0) for r in umum]
            avg_t = round(sum(t3_sent) / len(t3_sent), 3) if t3_sent else 0
            avg_u = round(sum(umum_sent) / len(umum_sent), 3) if umum_sent else 0
            lines.append(f"| Sentimen rata-rata | {avg_t} | {avg_u} |")

        return "\n".join(lines)

    def _section_g(self, trend_data) -> str:
        """Bagian G: Tren."""
        lines = []

        if not trend_data:
            lines.append("_Belum ada data tren._")
            return "\n".join(lines)

        periods = trend_data.get("periods", [])
        counts = trend_data.get("counts", [])

        if periods and counts:
            lines.append("### Volume per Bulan\n")
            lines.append("| Periode | Jumlah Konten |")
            lines.append("|---------|---------------|")
            for p, c in zip(periods, counts):
                bar = "█" * min(c, 50)
                lines.append(f"| {p} | {c} {bar} |")

        return "\n".join(lines)

    def _summary(self, pp_summary, demo_summary, analysis_results) -> str:
        """Ringkasan temuan utama."""
        lines = []

        # Top pain point
        top_pps = pp_summary.get("top_pain_points", [])
        if top_pps:
            pp_key, pp_data = top_pps[0]
            lines.append(
                f"1. **Pain point utama:** {pp_data['icon']} {pp_data['name']} "
                f"({pp_data['count']} konten)"
            )

        # Top demographic
        ranking = demo_summary.get("ranking", [])
        if ranking:
            key, data = ranking[0]
            lines.append(
                f"2. **Kelompok paling terdampak:** {data['icon']} {data['name']} "
                f"({data['count']} konten)"
            )

        # Abandonment
        total_abd = pp_summary.get("total_with_abandonment", 0)
        if total_abd:
            lines.append(
                f"3. **Sinyal abandonment:** {total_abd} konten mengandung "
                f"indikasi warga enggan/malas menggunakan layanan"
            )

        # Pusat vs Daerah
        pusat_n = sum(1 for r in analysis_results if r.get("gov_level") == "pusat")
        daerah_n = sum(1 for r in analysis_results if r.get("gov_level") == "daerah")
        if pusat_n or daerah_n:
            lines.append(
                f"4. **Distribusi:** {pusat_n} konten terkait Pusat, "
                f"{daerah_n} terkait Daerah"
            )

        return "\n".join(lines)

    def export_csv(self, analysis_results: list[dict], filename: str = None):
        """Export hasil analisis ke CSV."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analisis_{timestamp}.csv"

        filepath = self.exports_dir / filename

        if not analysis_results:
            print("Tidak ada data untuk diekspor.")
            return

        # Tentukan kolom
        columns = [
            "title", "url", "source_type", "source_name", "published_date",
            "category", "sub_issue", "gov_level", "area_type", "service_type",
            "province", "sentiment", "sentiment_score",
            "pain_points", "demographics",
            "has_abandonment_signal", "has_bottleneck",
        ]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            for result in analysis_results:
                # Flatten beberapa field
                row = dict(result)
                if isinstance(row.get("pain_points"), list):
                    row["pain_points"] = "; ".join(
                        pp.get("name", "") for pp in row["pain_points"]
                    )
                if isinstance(row.get("demographics"), list):
                    row["demographics"] = "; ".join(row["demographics"])
                writer.writerow(row)

        print(f"✅ CSV diekspor: {filepath}")
        return str(filepath)

    def generate_charts(self, analysis_results: list[dict]):
        """Generate chart visualisasi."""
        try:
            import matplotlib
            matplotlib.use("Agg")  # non-interactive backend
            import matplotlib.pyplot as plt

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 1. Distribusi kategori
            cat_counts = defaultdict(int)
            for r in analysis_results:
                cat = r.get("category", "lainnya")
                cat_name = CATEGORIES.get(cat, {}).get("name", cat)
                cat_counts[cat_name] += 1

            if cat_counts:
                fig, ax = plt.subplots(figsize=(10, 6))
                names = list(cat_counts.keys())
                values = list(cat_counts.values())
                colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"]
                ax.barh(names, values, color=colors[:len(names)])
                ax.set_xlabel("Jumlah Konten")
                ax.set_title("Distribusi Konten per Kategori")
                plt.tight_layout()
                chart_path = self.output_dir / f"chart_kategori_{timestamp}.png"
                plt.savefig(chart_path, dpi=150)
                plt.close()
                print(f"  📊 Chart kategori: {chart_path}")

            # 2. Distribusi sentimen
            sent_counts = defaultdict(int)
            for r in analysis_results:
                sent_counts[r.get("sentiment", "netral")] += 1

            if sent_counts:
                fig, ax = plt.subplots(figsize=(8, 8))
                labels = list(sent_counts.keys())
                sizes = list(sent_counts.values())
                colors_pie = {"positif": "#4ECDC4", "netral": "#95A5A6", "negatif": "#FF6B6B"}
                pie_colors = [colors_pie.get(l, "#95A5A6") for l in labels]
                ax.pie(sizes, labels=labels, colors=pie_colors,
                       autopct="%1.1f%%", startangle=90)
                ax.set_title("Distribusi Sentimen")
                chart_path = self.output_dir / f"chart_sentimen_{timestamp}.png"
                plt.savefig(chart_path, dpi=150)
                plt.close()
                print(f"  📊 Chart sentimen: {chart_path}")

            # 3. Pusat vs Daerah
            gov_counts = defaultdict(int)
            for r in analysis_results:
                gov_counts[r.get("gov_level", "tidak_teridentifikasi")] += 1

            if gov_counts:
                fig, ax = plt.subplots(figsize=(8, 6))
                labels = list(gov_counts.keys())
                values = list(gov_counts.values())
                ax.bar(labels, values, color=["#3498DB", "#E74C3C", "#95A5A6"])
                ax.set_ylabel("Jumlah Konten")
                ax.set_title("Distribusi Pusat vs Daerah")
                plt.tight_layout()
                chart_path = self.output_dir / f"chart_gov_level_{timestamp}.png"
                plt.savefig(chart_path, dpi=150)
                plt.close()
                print(f"  📊 Chart gov level: {chart_path}")

        except ImportError:
            print("⚠️ matplotlib tidak terinstall — skip chart generation")
