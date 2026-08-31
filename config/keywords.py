"""
Keyword pencarian per kategori dan sub-isu.
Digunakan oleh semua scraper untuk membangun query pencarian.
"""

CATEGORIES = {
    # ─── 🏥 KESEHATAN ─────────────────────────────────────────────────
    "kesehatan": {
        "name": "Kesehatan",
        "icon": "🏥",
        "sub_issues": {
            "rs_berkualitas": {
                "name": "Pembangunan RS Lengkap Berkualitas di Kab/Kota",
                "keywords": [
                    "rumah sakit data pasien kabupaten",
                    "BPJS data tidak sinkron",
                    "NIK tidak terdaftar BPJS",
                    "rumah sakit kabupaten kota kualitas",
                    "RS daerah fasilitas kurang",
                    "rujukan BPJS rumah sakit",
                    "antrian rumah sakit BPJS",
                ],
            },
            "pemeriksaan_gratis": {
                "name": "Pemeriksaan Kesehatan Gratis",
                "keywords": [
                    "pemeriksaan kesehatan gratis data",
                    "cek kesehatan gratis NIK",
                    "screening kesehatan data kependudukan",
                    "pemeriksaan gratis puskesmas",
                    "layanan kesehatan gratis syarat",
                ],
            },
            "penuntasan_tbc": {
                "name": "Penuntasan TBC",
                "keywords": [
                    "TBC data kesehatan",
                    "tuberkulosis pendataan",
                    "TBC Indonesia program",
                    "pengobatan TBC gratis",
                    "eliminasi TBC data",
                ],
            },
            "kelengkapan_data_rs": {
                "name": "Kelengkapan Data RS",
                "keywords": [
                    "data rumah sakit tidak lengkap",
                    "rekam medis pindah RS",
                    "pindah rumah sakit data pasien",
                    "data RS tidak terintegrasi",
                    "riwayat medis hilang",
                    "rekam medis elektronik",
                ],
            },
            "supply_chain_farmasi": {
                "name": "Supply Chain Farmasi dan Alkes",
                "keywords": [
                    "obat distribusi data",
                    "alat kesehatan ketersediaan",
                    "obat kosong rumah sakit",
                    "distribusi obat daerah",
                    "ketersediaan alkes puskesmas",
                ],
            },
        },
    },

    # ─── 🍚 PANGAN ────────────────────────────────────────────────────
    "pangan": {
        "name": "Pangan",
        "icon": "🍚",
        "sub_issues": {
            "sentra_produksi": {
                "name": "Kawasan Sentra Produksi Pangan / Lumbung Pangan",
                "keywords": [
                    "lumbung pangan data",
                    "ketahanan pangan pendataan",
                    "sentra produksi pangan daerah",
                    "food estate Indonesia",
                    "lumbung pangan nasional",
                ],
            },
            "makan_bergizi_gratis": {
                "name": "Makan Bergizi Gratis",
                "keywords": [
                    "makan bergizi gratis data penerima",
                    "MBG NIK",
                    "makan gratis salah sasaran",
                    "makan bergizi gratis sekolah",
                    "MBG pendataan siswa",
                    "program makan gratis masalah",
                    "makan bergizi gratis keluhan",
                ],
            },
        },
    },

    # ─── 📚 PENDIDIKAN ────────────────────────────────────────────────
    "pendidikan": {
        "name": "Pendidikan",
        "icon": "📚",
        "sub_issues": {
            "sekolah_unggul": {
                "name": "Penyelenggaraan Sekolah Unggul",
                "keywords": [
                    "sekolah unggul data siswa",
                    "PPDB data kependudukan",
                    "PPDB zonasi masalah",
                    "daftar sekolah NIK",
                    "penerimaan siswa baru data",
                    "PPDB online error",
                    "sekolah unggulan akses",
                ],
            },
            "revitalisasi_sarpras": {
                "name": "Revitalisasi Sarpras Sekolah",
                "keywords": [
                    "sarana prasarana sekolah data",
                    "sekolah rusak pendataan",
                    "revitalisasi sekolah daerah",
                    "infrastruktur sekolah tertinggal",
                    "sekolah roboh rusak berat",
                    "DAK pendidikan infrastruktur",
                ],
            },
        },
    },

    # ─── 🤝 KESEJAHTERAAN ─────────────────────────────────────────────
    "kesejahteraan": {
        "name": "Kesejahteraan",
        "icon": "🤝",
        "sub_issues": {
            "bansos_adaptif": {
                "name": "Penyaluran Bansos Adaptif",
                "keywords": [
                    "bansos data tidak valid",
                    "bantuan sosial salah sasaran",
                    "DTKS tidak akurat",
                    "bansos tidak tepat sasaran",
                    "data terpadu kesejahteraan sosial",
                    "penerima bansos ganda",
                    "bansos tidak dapat padahal miskin",
                    "verifikasi validasi DTKS",
                ],
            },
            "kartu_usaha_afirmatif": {
                "name": "Kartu Usaha Afirmatif",
                "keywords": [
                    "kartu usaha afirmatif data",
                    "usaha mikro NIK pendaftaran",
                    "kartu usaha UMKM data",
                    "program usaha rakyat pendataan",
                ],
            },
            "kartu_usaha_produktif": {
                "name": "Kartu Usaha Produktif",
                "keywords": [
                    "KUR data nasabah",
                    "usaha produktif pendataan",
                    "kredit usaha rakyat masalah",
                    "KUR syarat data",
                    "pinjaman usaha mikro NIK",
                ],
            },
            "kesejahteraan_asn": {
                "name": "Peningkatan Kesejahteraan ASN",
                "keywords": [
                    "ASN data kepegawaian",
                    "PNS administrasi masalah",
                    "tunjangan ASN data",
                    "gaji PNS data tidak sinkron",
                    "BKN data kepegawaian",
                ],
            },
        },
    },

    # ─── 🛣️ INFRASTRUKTUR ─────────────────────────────────────────────
    "infrastruktur": {
        "name": "Infrastruktur",
        "icon": "🛣️",
        "sub_issues": {
            "layanan_dasar_desa": {
                "name": "Pemenuhan Layanan Dasar dan Infrastruktur Desa",
                "keywords": [
                    "desa layanan dasar data",
                    "infrastruktur desa pendataan",
                    "dana desa infrastruktur",
                    "desa tertinggal layanan",
                    "desa 3T infrastruktur",
                    "akses layanan publik desa",
                ],
            },
            "perumahan_terintegrasi": {
                "name": "Penyediaan Perumahan Terintegrasi",
                "keywords": [
                    "perumahan data kependudukan",
                    "rumah subsidi NIK",
                    "KPR data tidak sinkron",
                    "program perumahan rakyat data",
                    "rumah susun pendataan",
                    "FLPP rumah subsidi masalah",
                ],
            },
        },
    },

    # ─── 💰 PENERIMAAN NEGARA ─────────────────────────────────────────
    "penerimaan_negara": {
        "name": "Penerimaan Negara",
        "icon": "💰",
        "sub_issues": {
            "penerimaan_pajak": {
                "name": "Ekstensifikasi dan Intensifikasi Penerimaan Pajak",
                "keywords": [
                    "pajak data tidak sinkron",
                    "NPWP NIK integrasi",
                    "wajib pajak data",
                    "pajak NIK NPWP masalah",
                    "coretax system masalah",
                    "coretax error",
                    "DJP online data",
                    "lapor pajak online error",
                ],
            },
            "intensifikasi_pnbp": {
                "name": "Intensifikasi PNBP",
                "keywords": [
                    "PNBP data",
                    "penerimaan negara bukan pajak pendataan",
                    "PNBP optimalisasi",
                    "retribusi daerah data",
                ],
            },
        },
    },
}


# ─── Keyword gabungan untuk pencarian umum ────────────────────────────
# Digunakan saat scraper ingin mencari semua topik sekaligus

GENERAL_KEYWORDS = [
    "layanan publik masalah data",
    "pelayanan publik keluhan",
    "data kependudukan tidak sinkron",
    "NIK tidak terdaftar",
    "birokrasi berbelit",
    "layanan pemerintah susah",
    "pelayanan publik digital error",
    "administrasi kependudukan masalah",
    "KTP elektronik masalah",
    "data dukcapil tidak sinkron",
    "integrasi data pemerintah",
    "satu data Indonesia masalah",
    "pelayanan publik daerah",
    "pelayanan publik pusat",
]


def get_all_keywords() -> list[str]:
    """Ambil semua keyword dari semua kategori + general."""
    keywords = list(GENERAL_KEYWORDS)
    for cat_data in CATEGORIES.values():
        for sub in cat_data["sub_issues"].values():
            keywords.extend(sub["keywords"])
    # Deduplicate sambil jaga urutan
    seen = set()
    unique = []
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower not in seen:
            seen.add(kw_lower)
            unique.append(kw)
    return unique


def get_keywords_for_category(category: str) -> list[str]:
    """Ambil semua keyword untuk satu kategori."""
    cat_data = CATEGORIES.get(category)
    if not cat_data:
        raise ValueError(f"Kategori tidak dikenal: {category}. "
                         f"Pilihan: {list(CATEGORIES.keys())}")
    keywords = []
    for sub in cat_data["sub_issues"].values():
        keywords.extend(sub["keywords"])
    return keywords
