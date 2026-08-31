"""
Pain Point Extractor — modul inti analisis.

Mendeteksi dan mengkategorikan pain point spesifik dari teks:
1. Data tidak valid / tidak sinkron
2. Verifikasi manual berulang
3. Bolak-balik antar instansi
4. Persyaratan dokumen berlebihan
5. Sistem digital tidak berfungsi
6. Salah sasaran penerima manfaat

Juga mendeteksi:
- Sinyal abandonment (warga "malas menggunakan")
- Bottleneck (titik waktu paling terbuang)
"""

from config.classifiers import (
    PAIN_POINT_PATTERNS,
    ABANDONMENT_SIGNALS,
    BOTTLENECK_PATTERNS,
)


class PainPointExtractor:
    """Ekstraksi pain point dari teks."""

    def extract(self, text: str) -> dict:
        """
        Ekstrak semua pain point, sinyal abandonment, dan bottleneck.
        
        Returns:
            {
                "pain_points": [
                    {"type": "data_tidak_valid", "name": "...", "matches": [...]},
                    ...
                ],
                "abandonment": {
                    "detected": bool,
                    "signals": [str, ...]
                },
                "bottleneck": {
                    "detected": bool,
                    "patterns": [str, ...]
                },
            }
        """
        if not text:
            return {
                "pain_points": [],
                "abandonment": {"detected": False, "signals": []},
                "bottleneck": {"detected": False, "patterns": []},
            }

        text_lower = text.lower()

        return {
            "pain_points": self._detect_pain_points(text_lower),
            "abandonment": self._detect_abandonment(text_lower),
            "bottleneck": self._detect_bottleneck(text_lower),
        }

    def _detect_pain_points(self, text: str) -> list[dict]:
        """Deteksi semua tipe pain point."""
        found = []

        for pp_key, pp_data in PAIN_POINT_PATTERNS.items():
            matches = []
            for pattern in pp_data["patterns"]:
                if pattern.lower() in text:
                    matches.append(pattern)

            if matches:
                found.append({
                    "type": pp_key,
                    "name": pp_data["name"],
                    "icon": pp_data["icon"],
                    "matches": matches,
                    "match_count": len(matches),
                })

        # Sort by match count descending
        found.sort(key=lambda x: x["match_count"], reverse=True)
        return found

    def _detect_abandonment(self, text: str) -> dict:
        """Deteksi sinyal warga 'malas menggunakan' layanan."""
        signals = [s for s in ABANDONMENT_SIGNALS if s.lower() in text]
        return {
            "detected": len(signals) > 0,
            "signals": signals,
        }

    def _detect_bottleneck(self, text: str) -> dict:
        """Deteksi indikasi waktu terbuang / bottleneck."""
        patterns = [p for p in BOTTLENECK_PATTERNS if p.lower() in text]
        return {
            "detected": len(patterns) > 0,
            "patterns": patterns,
        }

    def get_pain_point_summary(self, results: list[dict]) -> dict:
        """
        Agregasi pain point dari banyak artikel.
        
        Args:
            results: List of extract() results
            
        Returns:
            {
                "by_type": {
                    "data_tidak_valid": {"count": 45, "name": "...", ...},
                    ...
                },
                "total_with_pain_points": int,
                "total_with_abandonment": int,
                "total_with_bottleneck": int,
                "top_pain_points": [(type, count), ...],
                "top_abandonment_signals": [(signal, count), ...],
                "top_bottleneck_patterns": [(pattern, count), ...],
            }
        """
        type_counts = {}
        abandonment_count = 0
        bottleneck_count = 0
        signal_counts = {}
        pattern_counts = {}

        for result in results:
            # Pain points
            for pp in result.get("pain_points", []):
                pp_type = pp["type"]
                if pp_type not in type_counts:
                    type_counts[pp_type] = {
                        "count": 0,
                        "name": pp["name"],
                        "icon": pp["icon"],
                    }
                type_counts[pp_type]["count"] += 1

            # Abandonment
            abd = result.get("abandonment", {})
            if abd.get("detected"):
                abandonment_count += 1
                for sig in abd.get("signals", []):
                    signal_counts[sig] = signal_counts.get(sig, 0) + 1

            # Bottleneck
            bn = result.get("bottleneck", {})
            if bn.get("detected"):
                bottleneck_count += 1
                for pat in bn.get("patterns", []):
                    pattern_counts[pat] = pattern_counts.get(pat, 0) + 1

        return {
            "by_type": type_counts,
            "total_with_pain_points": sum(
                1 for r in results if r.get("pain_points")
            ),
            "total_with_abandonment": abandonment_count,
            "total_with_bottleneck": bottleneck_count,
            "top_pain_points": sorted(
                type_counts.items(),
                key=lambda x: x[1]["count"],
                reverse=True,
            ),
            "top_abandonment_signals": sorted(
                signal_counts.items(), key=lambda x: x[1], reverse=True
            )[:10],
            "top_bottleneck_patterns": sorted(
                pattern_counts.items(), key=lambda x: x[1], reverse=True
            )[:10],
        }
