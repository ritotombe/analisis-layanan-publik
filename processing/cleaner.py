"""
Text cleaner — pembersihan dan normalisasi teks Bahasa Indonesia.

Menangani: HTML, URL, emoji, slang, stemming, stopwords.
"""

import re
import html as html_lib


# ── Kamus normalisasi slang/informal → baku ──────────────────────────
SLANG_MAP = {
    "gak": "tidak", "ga": "tidak", "gk": "tidak", "nggak": "tidak",
    "ngga": "tidak", "kagak": "tidak", "kaga": "tidak",
    "gw": "saya", "gue": "saya", "ane": "saya",
    "lu": "kamu", "lo": "kamu", "elu": "kamu", "ente": "kamu",
    "emang": "memang", "emg": "memang",
    "udah": "sudah", "udh": "sudah", "sdh": "sudah",
    "bgt": "banget", "bener": "benar", "bnr": "benar",
    "ribet": "rumit", "ruwet": "rumit",
    "ngurus": "mengurus", "ngurusin": "mengurusi",
    "nanya": "bertanya", "nanyain": "menanyakan",
    "bikin": "membuat", "bkin": "membuat",
    "dapet": "dapat", "dpt": "dapat",
    "pake": "pakai", "pk": "pakai",
    "cuma": "hanya", "cm": "hanya",
    "gimana": "bagaimana", "gmn": "bagaimana",
    "kenapa": "mengapa", "knp": "mengapa",
    "kayak": "seperti", "kyk": "seperti",
    "banget": "sangat", "bgt": "sangat",
    "aja": "saja", "aj": "saja",
    "kalo": "kalau", "kl": "kalau",
    "trus": "terus", "trs": "terus",
    "jg": "juga", "jga": "juga",
    "yg": "yang", "yng": "yang",
    "dgn": "dengan", "dg": "dengan",
    "org": "orang", "orng": "orang",
    "krn": "karena", "krna": "karena",
    "blm": "belum", "blum": "belum",
    "hrs": "harus", "hrus": "harus",
    "bs": "bisa", "bsa": "bisa",
    "msh": "masih", "masi": "masih",
    "smua": "semua", "smw": "semua",
    "bnyk": "banyak", "byk": "banyak",
    "susah": "sulit",
    "males": "malas",
    "nyerah": "menyerah",
    "kapok": "jera",
    "ojol": "ojek online",
}

# ── Indonesian stopwords ──────────────────────────────────────────────
STOPWORDS_ID = {
    "yang", "dan", "di", "ke", "dari", "ini", "itu", "dengan",
    "untuk", "pada", "adalah", "akan", "dalam", "oleh", "karena",
    "atau", "jika", "maka", "bahwa", "setelah", "saat", "ketika",
    "ada", "bisa", "sudah", "belum", "hanya", "juga", "telah",
    "lebih", "paling", "serta", "antara", "seperti", "melalui",
    "sebagai", "tentang", "namun", "tetapi", "sehingga", "agar",
    "secara", "terhadap", "hingga", "sejak", "selama", "sambil",
    "mereka", "kami", "kita", "dia", "ia", "nya", "tersebut",
    "lain", "hal", "banyak", "beberapa", "sangat", "yaitu",
    "kalau", "masih", "bisa", "harus", "perlu", "dapat",
}


class TextCleaner:
    """Pembersih teks untuk Bahasa Indonesia."""

    def __init__(self, use_stemmer: bool = True):
        self.stemmer = None
        if use_stemmer:
            try:
                from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
                factory = StemmerFactory()
                self.stemmer = factory.create_stemmer()
            except ImportError:
                pass  # Sastrawi opsional

    def clean(self, text: str, stem: bool = False) -> str:
        """
        Pipeline pembersihan teks lengkap.
        
        Args:
            text: Teks mentah
            stem: Apakah perlu stemming (lambat, gunakan hanya untuk analisis)
            
        Returns:
            Teks bersih
        """
        if not text:
            return ""

        text = self._unescape_html(text)
        text = self._remove_html_tags(text)
        text = self._remove_urls(text)
        text = self._remove_emails(text)
        text = self._handle_emojis(text)
        text = self._normalize_slang(text)
        text = self._remove_special_chars(text)
        text = self._normalize_whitespace(text)

        if stem and self.stemmer:
            text = self.stemmer.stem(text)

        return text.strip()

    def clean_for_analysis(self, text: str) -> str:
        """Pembersihan ringan — pertahankan kata-kata penting untuk analisis."""
        if not text:
            return ""

        text = self._unescape_html(text)
        text = self._remove_html_tags(text)
        text = self._remove_urls(text)
        text = self._normalize_slang(text)
        text = self._normalize_whitespace(text)
        return text.strip()

    def remove_stopwords(self, text: str) -> str:
        """Hapus stopwords Bahasa Indonesia."""
        words = text.lower().split()
        return " ".join(w for w in words if w not in STOPWORDS_ID)

    # ── Private methods ──────────────────────────────────────────────

    def _unescape_html(self, text: str) -> str:
        return html_lib.unescape(text)

    def _remove_html_tags(self, text: str) -> str:
        return re.sub(r"<[^>]+>", " ", text)

    def _remove_urls(self, text: str) -> str:
        return re.sub(
            r"https?://\S+|www\.\S+", " ", text
        )

    def _remove_emails(self, text: str) -> str:
        return re.sub(r"\S+@\S+\.\S+", " ", text)

    def _handle_emojis(self, text: str) -> str:
        """Konversi emoji umum ke token teks."""
        emoji_map = {
            "😡": " marah ",
            "😤": " kesal ",
            "😢": " sedih ",
            "😭": " sangat_sedih ",
            "👍": " bagus ",
            "👎": " jelek ",
            "💔": " kecewa ",
            "🙏": " mohon ",
            "😊": " senang ",
            "😠": " marah ",
            "🤬": " sangat_marah ",
            "😩": " frustrasi ",
            "🤦": " kecewa ",
        }
        for emoji, token in emoji_map.items():
            text = text.replace(emoji, token)
        # Hapus emoji lain
        text = re.sub(
            r"[\U00010000-\U0010ffff]", " ", text, flags=re.UNICODE
        )
        return text

    def _normalize_slang(self, text: str) -> str:
        """Normalisasi kata slang ke baku."""
        words = text.split()
        normalized = []
        for word in words:
            lower = word.lower().strip(".,!?;:\"'()")
            if lower in SLANG_MAP:
                normalized.append(SLANG_MAP[lower])
            else:
                normalized.append(word)
        return " ".join(normalized)

    def _remove_special_chars(self, text: str) -> str:
        """Hapus karakter spesial, pertahankan huruf, angka, spasi."""
        return re.sub(r"[^a-zA-Z0-9\s\-]", " ", text)

    def _normalize_whitespace(self, text: str) -> str:
        """Normalisasi whitespace berlebihan."""
        return re.sub(r"\s+", " ", text)
