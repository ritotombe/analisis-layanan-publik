"""
Multi-dimensional classifier — klasifikasi artikel ke:
1. Kategori (6 kategori program)
2. Sub-isu spesifik
3. Level pemerintah (pusat vs daerah)
4. Tipe wilayah (3T vs umum)
5. Tipe layanan (digital vs umum/offline)
6. Provinsi (jika teridentifikasi)
"""

from config.keywords import CATEGORIES
from config.classifiers import (
    PUSAT_KEYWORDS,
    DAERAH_KEYWORDS,
    KEYWORDS_3T,
    KABUPATEN_3T_SAMPLE,
    DIGITAL_KEYWORDS,
    UMUM_OFFLINE_KEYWORDS,
    PROVINCES,
    PROVINCE_ALIASES,
)


class ArticleClassifier:
    """Klasifikasi multi-dimensi untuk artikel/konten."""

    def classify(self, text: str) -> dict:
        """
        Klasifikasi teks ke semua dimensi.
        
        Returns:
            {
                "category": str,
                "sub_issue": str,
                "gov_level": str,
                "area_type": str,
                "service_type": str,
                "province": str,
                "source_type": str,  (diisi oleh caller)
            }
        """
        text_lower = text.lower()

        return {
            "category": self._classify_category(text_lower),
            "sub_issue": self._classify_sub_issue(text_lower),
            "gov_level": self._classify_gov_level(text_lower),
            "area_type": self._classify_area_type(text_lower),
            "service_type": self._classify_service_type(text_lower),
            "province": self._detect_province(text_lower),
        }

    def _classify_category(self, text: str) -> str:
        """Tentukan kategori utama berdasarkan keyword match terbanyak."""
        scores = {}
        for cat_key, cat_data in CATEGORIES.items():
            score = 0
            for sub in cat_data["sub_issues"].values():
                for kw in sub["keywords"]:
                    if kw.lower() in text:
                        score += 2  # exact keyword match
                    else:
                        # Cek per kata
                        kw_words = kw.lower().split()
                        matches = sum(1 for w in kw_words if w in text)
                        if matches >= len(kw_words) * 0.6:
                            score += 1
            scores[cat_key] = score

        if not scores or max(scores.values()) == 0:
            return "tidak_teridentifikasi"

        return max(scores, key=scores.get)

    def _classify_sub_issue(self, text: str) -> str:
        """Tentukan sub-isu spesifik."""
        best_sub = "tidak_teridentifikasi"
        best_score = 0

        for cat_data in CATEGORIES.values():
            for sub_key, sub_data in cat_data["sub_issues"].items():
                score = 0
                for kw in sub_data["keywords"]:
                    if kw.lower() in text:
                        score += 2
                    else:
                        kw_words = kw.lower().split()
                        matches = sum(1 for w in kw_words if w in text)
                        if matches >= len(kw_words) * 0.6:
                            score += 1
                if score > best_score:
                    best_score = score
                    best_sub = sub_key

        return best_sub

    def _classify_gov_level(self, text: str) -> str:
        """Klasifikasi pusat vs daerah."""
        pusat_score = sum(
            1 for kw in PUSAT_KEYWORDS if kw.lower() in text
        )
        daerah_score = sum(
            1 for kw in DAERAH_KEYWORDS if kw.lower() in text
        )

        if pusat_score > daerah_score:
            return "pusat"
        elif daerah_score > pusat_score:
            return "daerah"
        elif pusat_score > 0:
            return "pusat"  # tie-break ke pusat
        return "tidak_teridentifikasi"

    def _classify_area_type(self, text: str) -> str:
        """Klasifikasi 3T vs umum."""
        # Cek keyword 3T
        t3_score = sum(1 for kw in KEYWORDS_3T if kw.lower() in text)

        # Cek kabupaten 3T
        for kab in KABUPATEN_3T_SAMPLE:
            if kab.lower() in text:
                t3_score += 2

        if t3_score >= 1:
            return "3T"
        return "umum"

    def _classify_service_type(self, text: str) -> str:
        """Klasifikasi layanan digital vs umum (offline)."""
        digital_score = sum(
            1 for kw in DIGITAL_KEYWORDS if kw.lower() in text
        )
        offline_score = sum(
            1 for kw in UMUM_OFFLINE_KEYWORDS if kw.lower() in text
        )

        if digital_score > offline_score:
            return "digital"
        elif offline_score > digital_score:
            return "umum"
        return "tidak_teridentifikasi"

    def _detect_province(self, text: str) -> str:
        """Deteksi provinsi yang disebutkan dalam teks."""
        # Cek nama provinsi lengkap
        for province in PROVINCES:
            if province.lower() in text:
                return province

        # Cek alias
        for alias, province in PROVINCE_ALIASES.items():
            if alias.lower() in text:
                return province

        return ""
