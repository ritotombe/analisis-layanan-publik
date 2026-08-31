"""
Sentiment Analysis — analisis sentimen Bahasa Indonesia.

Mode:
1. Lexicon-based (default) — ringan, tanpa GPU
2. IndoBERT (opsional) — lebih akurat, butuh transformers + torch
"""


# ── Lexicon sentimen Bahasa Indonesia (konteks layanan publik) ────────

POSITIVE_WORDS = {
    # Umum
    "bagus", "baik", "senang", "puas", "lancar", "cepat", "mudah",
    "memuaskan", "terbantu", "berhasil", "sukses", "mantap",
    "responsif", "ramah", "helpful", "membantu", "efisien",
    "tepat", "akurat", "transparan", "profesional",
    "terima kasih", "appreciate", "terbaik", "luar biasa",
    "excellent", "recommended", "rekomen",
    # Konteks layanan
    "terintegrasi", "sinkron", "otomatis", "digital",
    "tanpa antri", "cepat selesai", "satu hari jadi",
    "gratis", "tidak dipungut biaya",
}

NEGATIVE_WORDS = {
    # Umum
    "buruk", "jelek", "kecewa", "susah", "sulit", "lambat",
    "lama", "ribet", "rumit", "berbelit", "berbelit-belit",
    "gagal", "error", "rusak", "tidak bisa", "tidak berfungsi",
    "payah", "parah", "zonk", "sampah", "bohong", "tipu",
    # Frustrasi
    "frustrasi", "frustasi", "kesal", "marah", "jengkel",
    "capek", "cape", "lelah", "bosan",
    "malas", "males", "ogah", "kapok", "jera",
    "menyerah", "pasrah",
    # Keluhan spesifik
    "tidak sinkron", "tidak terintegrasi", "tidak akurat",
    "salah sasaran", "data salah", "data ganda",
    "bolak-balik", "mondar-mandir",
    "antri lama", "tunggu lama", "berhari-hari",
    "fotokopi", "diminta ulang",
    "server down", "error terus", "crash",
    "dilempar", "disuruh ke",
    "korupsi", "pungli", "pungutan liar",
    # Intensifier negatif
    "sangat buruk", "sangat kecewa", "sangat lambat",
    "tidak berguna", "buang waktu", "sia-sia",
}

INTENSIFIERS = {
    "sangat": 1.5, "banget": 1.5, "sekali": 1.4,
    "amat": 1.5, "super": 1.6, "paling": 1.5,
    "terlalu": 1.3, "begitu": 1.2, "sungguh": 1.4,
    "luar biasa": 1.6, "extremely": 1.7,
}

NEGATORS = {
    "tidak", "bukan", "belum", "jangan", "tanpa",
    "tak", "tiada", "non",
}


class SentimentAnalyzer:
    """Analisis sentimen lexicon-based untuk Bahasa Indonesia."""

    def analyze(self, text: str) -> dict:
        """
        Analisis sentimen teks.
        
        Returns:
            {
                "sentiment": "positif" | "netral" | "negatif",
                "score": float (-1.0 to 1.0),
                "positive_count": int,
                "negative_count": int,
            }
        """
        if not text:
            return {
                "sentiment": "netral",
                "score": 0.0,
                "positive_count": 0,
                "negative_count": 0,
            }

        text_lower = text.lower()
        words = text_lower.split()

        pos_count = 0
        neg_count = 0
        pos_score = 0.0
        neg_score = 0.0

        for i, word in enumerate(words):
            multiplier = 1.0

            # Cek intensifier sebelumnya
            if i > 0 and words[i - 1] in INTENSIFIERS:
                multiplier = INTENSIFIERS[words[i - 1]]

            # Cek negator sebelumnya (membalik sentimen)
            is_negated = False
            if i > 0 and words[i - 1] in NEGATORS:
                is_negated = True
            elif i > 1 and words[i - 2] in NEGATORS:
                is_negated = True

            if word in POSITIVE_WORDS:
                if is_negated:
                    neg_count += 1
                    neg_score += multiplier
                else:
                    pos_count += 1
                    pos_score += multiplier
            elif word in NEGATIVE_WORDS:
                if is_negated:
                    pos_count += 1
                    pos_score += multiplier
                else:
                    neg_count += 1
                    neg_score += multiplier

        # Cek frase multi-kata
        for phrase in POSITIVE_WORDS:
            if " " in phrase and phrase in text_lower:
                pos_count += 1
                pos_score += 1.0
        for phrase in NEGATIVE_WORDS:
            if " " in phrase and phrase in text_lower:
                neg_count += 1
                neg_score += 1.0

        # Hitung skor akhir
        total = pos_score + neg_score
        if total == 0:
            score = 0.0
        else:
            score = (pos_score - neg_score) / total  # -1.0 to 1.0

        # Tentukan label
        if score > 0.1:
            sentiment = "positif"
        elif score < -0.1:
            sentiment = "negatif"
        else:
            sentiment = "netral"

        return {
            "sentiment": sentiment,
            "score": round(score, 3),
            "positive_count": pos_count,
            "negative_count": neg_count,
        }
