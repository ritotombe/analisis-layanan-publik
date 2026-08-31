import json
import logging
import os
import time
from typing import Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from config.settings import GEMINI_API_KEY
from config.keywords import CATEGORIES
from config.classifiers import PAIN_POINT_PATTERNS, DEMOGRAPHIC_GROUPS

logger = logging.getLogger(__name__)

# Cache valid categories to prompt
VALID_CATEGORIES = list(CATEGORIES.keys())
VALID_PAIN_POINTS = list(PAIN_POINT_PATTERNS.keys())
VALID_DEMOGRAPHICS = list(DEMOGRAPHIC_GROUPS.keys())

PROMPT_TEMPLATE = """
Anda adalah asisten AI analis layanan publik Indonesia.
Tugas Anda adalah membaca teks berita atau ulasan aplikasi berikut dan mengekstrak informasi ke dalam format JSON yang valid.

TEKS:
"{text}"

KATEGORI YANG DIIZINKAN: {categories}
PAIN POINTS YANG DIIZINKAN: {pain_points}
DEMOGRAFI YANG DIIZINKAN: {demographics}

FORMAT JSON YANG DIHARAPKAN:
{{
    "category": "salah satu dari kategori diizinkan, atau 'tidak_teridentifikasi'",
    "sub_issue": "string singkat (maks 3 kata, huruf kecil, pisah underscore) mendeskripsikan sub-isu spesifik. contoh: 'antrean_rs', 'verifikasi_nik'",
    "gov_level": "'pusat', 'daerah', atau 'tidak_teridentifikasi'",
    "area_type": "'3T', 'umum', atau 'tidak_teridentifikasi'",
    "service_type": "'digital', 'umum', atau 'tidak_teridentifikasi'",
    "province": "Nama provinsi jika disebutkan (misal: 'Jawa Barat'), atau kosong ''",
    "sentiment": "'positif', 'netral', atau 'negatif'",
    "sentiment_score": float antara -1.0 (sangat negatif) sampai 1.0 (sangat positif),
    "pain_points": ["pilih dari pain points diizinkan, jika relevan. Jika tidak ada, array kosong"],
    "demographics": ["pilih dari demografi diizinkan, jika secara eksplisit atau implisit dibahas. Jika tidak, array kosong"],
    "has_abandonment_signal": 1 jika ada indikasi warga menyerah/malas/pilih calo, jika tidak 0,
    "has_bottleneck": 1 jika ada indikasi waktu tunggu lama/proses lambat berlarut-larut, jika tidak 0
}}

PENTING:
- Kembalikan HANYA JSON yang valid, tanpa teks markdown atau blok backticks (```json ... ```).
- Pastikan memahami sarkasme atau konteks tersirat dalam sentimen dan abandonment.
"""

class LLMEnhancer:
    def __init__(self):
        self.enabled = False
        if genai and GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-3.5-flash')
            self.enabled = True
            logger.info("✅ Gemini AI Enhancer aktif.")
        else:
            logger.warning("⚠️ Gemini API Key tidak diset atau google-generativeai tidak terinstall. LLM Enhancer dinonaktifkan.")

    def analyze_text(self, title: str, body: str) -> Optional[dict]:
        if not self.enabled:
            return None

        text = f"Judul: {title}\n\nIsi: {body}"
        if len(text.strip()) < 10:
            return None

        prompt = PROMPT_TEMPLATE.format(
            text=text,
            categories=", ".join(VALID_CATEGORIES),
            pain_points=", ".join(VALID_PAIN_POINTS),
            demographics=", ".join(VALID_DEMOGRAPHICS),
        )

        try:
            # Panggil Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            
            result = json.loads(response.text)
            
            # Format agar sesuai dengan ekspektasi run_analyze.py
            result["pain_points_detail"] = [{"type": pp, "name": pp} for pp in result.get("pain_points", [])]
            result["demographics_detail"] = result.get("demographics", [])
            result["abandonment_signals_detail"] = ["sinyal_terdeteksi_ai"] if result.get("has_abandonment_signal") else []
            result["bottleneck_patterns_detail"] = ["hambatan_terdeteksi_ai"] if result.get("has_bottleneck") else []
            
            # Rate limiting safety for Free Tier (15 RPM)
            time.sleep(4.1)
            
            return result
        except Exception as e:
            logger.error(f"Gagal melakukan analisis LLM: {e}")
            return None
