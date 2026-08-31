"""
Trend Analyzer — analisis tren waktu.

Menganalisis volume, sentimen, dan pain point dari waktu ke waktu.
"""

from collections import defaultdict
from datetime import datetime


class TrendAnalyzer:
    """Analisis tren dari data yang sudah diproses."""

    def analyze_volume_trend(
        self,
        articles: list[dict],
        period: str = "monthly",
    ) -> dict:
        """
        Analisis tren volume artikel per periode.
        
        Args:
            articles: List of article dicts (harus punya 'published_date')
            period: 'daily', 'weekly', 'monthly'
            
        Returns:
            {
                "periods": ["2025-09", "2025-10", ...],
                "counts": [12, 15, ...],
                "by_category": {
                    "kesehatan": [5, 8, ...],
                    ...
                }
            }
        """
        period_counts = defaultdict(int)
        period_category = defaultdict(lambda: defaultdict(int))

        for article in articles:
            date_str = article.get("published_date", "")
            category = article.get("category", "lainnya")

            period_key = self._get_period_key(date_str, period)
            if period_key:
                period_counts[period_key] += 1
                period_category[period_key][category] += 1

        # Sort by period
        sorted_periods = sorted(period_counts.keys())

        # Kumpulkan kategori unik
        all_categories = set()
        for cats in period_category.values():
            all_categories.update(cats.keys())

        by_category = {}
        for cat in all_categories:
            by_category[cat] = [
                period_category[p].get(cat, 0) for p in sorted_periods
            ]

        return {
            "periods": sorted_periods,
            "counts": [period_counts[p] for p in sorted_periods],
            "by_category": by_category,
        }

    def analyze_sentiment_trend(
        self,
        articles: list[dict],
        period: str = "monthly",
    ) -> dict:
        """
        Analisis tren sentimen per periode.
        
        Returns:
            {
                "periods": [...],
                "avg_scores": [...],
                "positive_pct": [...],
                "negative_pct": [...],
            }
        """
        period_scores = defaultdict(list)
        period_sentiments = defaultdict(lambda: {"positif": 0, "negatif": 0, "netral": 0})

        for article in articles:
            date_str = article.get("published_date", "")
            score = article.get("sentiment_score", 0)
            sentiment = article.get("sentiment", "netral")

            period_key = self._get_period_key(date_str, period)
            if period_key:
                period_scores[period_key].append(score)
                period_sentiments[period_key][sentiment] += 1

        sorted_periods = sorted(period_scores.keys())

        avg_scores = []
        positive_pct = []
        negative_pct = []

        for p in sorted_periods:
            scores = period_scores[p]
            avg_scores.append(
                round(sum(scores) / len(scores), 3) if scores else 0
            )
            total = sum(period_sentiments[p].values())
            if total > 0:
                positive_pct.append(
                    round(period_sentiments[p]["positif"] / total * 100, 1)
                )
                negative_pct.append(
                    round(period_sentiments[p]["negatif"] / total * 100, 1)
                )
            else:
                positive_pct.append(0)
                negative_pct.append(0)

        return {
            "periods": sorted_periods,
            "avg_scores": avg_scores,
            "positive_pct": positive_pct,
            "negative_pct": negative_pct,
        }

    def detect_spikes(
        self,
        articles: list[dict],
        period: str = "weekly",
        threshold: float = 2.0,
    ) -> list[dict]:
        """
        Deteksi lonjakan volume yang tidak biasa.
        
        Spike = volume > rata-rata × threshold.
        """
        volume = self.analyze_volume_trend(articles, period)
        counts = volume["counts"]
        periods = volume["periods"]

        if not counts:
            return []

        avg = sum(counts) / len(counts)
        spikes = []

        for i, (p, c) in enumerate(zip(periods, counts)):
            if c > avg * threshold:
                spikes.append({
                    "period": p,
                    "count": c,
                    "average": round(avg, 1),
                    "ratio": round(c / avg, 1) if avg > 0 else 0,
                })

        return spikes

    def _get_period_key(self, date_str: str, period: str) -> str:
        """Konversi tanggal ke period key."""
        if not date_str:
            return ""
        try:
            # Coba beberapa format
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%d %B %Y"]:
                try:
                    dt = datetime.strptime(date_str[:19], fmt)
                    break
                except ValueError:
                    continue
            else:
                return ""

            if period == "daily":
                return dt.strftime("%Y-%m-%d")
            elif period == "weekly":
                return dt.strftime("%Y-W%W")
            else:  # monthly
                return dt.strftime("%Y-%m")

        except Exception:
            return ""
