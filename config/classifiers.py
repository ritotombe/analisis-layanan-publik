"""
Rules klasifikasi untuk 3 dimensi:
1. Level pemerintah: Pusat vs Daerah
2. Tipe wilayah: 3T vs Umum
3. Tipe layanan: Umum (offline) vs Digital

Plus: pattern untuk deteksi pain point dan kelompok demografis.
"""

# ═══════════════════════════════════════════════════════════════════════
# DIMENSI 1: PUSAT vs DAERAH
# ═══════════════════════════════════════════════════════════════════════

PUSAT_KEYWORDS = [
    # Lembaga pusat
    "pemerintah pusat", "kementerian", "presiden", "wakil presiden",
    "DPR RI", "DPD RI", "MPR", "kabinet",
    # Kementerian spesifik
    "kemenkeu", "kemenkes", "kemendikbud", "kemen PUPR",
    "kemendagri", "kemensos", "kemenag", "kemenhub",
    "kemenkominfo", "kemenperin", "kementan",
    "kementerian keuangan", "kementerian kesehatan",
    "kementerian pendidikan", "kementerian sosial",
    "kementerian dalam negeri", "kementerian pertanian",
    # Lembaga pusat
    "BKN", "BPJS pusat", "DJP", "direktorat jenderal",
    "badan pusat", "lembaga negara",
    "BAPPENAS", "BPS", "OJK", "BI ", "Bank Indonesia",
    # Program pusat
    "program nasional", "kebijakan nasional", "APBN",
    "peraturan presiden", "perpres", "PP ", "peraturan pemerintah",
    "instruksi presiden", "inpres",
]

DAERAH_KEYWORDS = [
    # Jabatan daerah
    "pemda", "pemerintah daerah", "gubernur", "wakil gubernur",
    "bupati", "wakil bupati", "walikota", "wakil walikota",
    "DPRD", "sekretaris daerah", "sekda",
    "camat", "lurah", "kepala desa", "kades",
    # Instansi daerah
    "dinas", "dinas kesehatan", "dinas pendidikan",
    "dinas sosial", "dinas kependudukan", "disdukcapil",
    "BPBD", "Bappeda",
    "puskesmas", "kelurahan", "kecamatan",
    "kantor desa", "kantor kelurahan", "kantor kecamatan",
    # Anggaran daerah
    "APBD", "dana desa", "DAK", "DAU", "dana alokasi",
    "perda", "peraturan daerah", "pergub", "perbup", "perwal",
]

# ═══════════════════════════════════════════════════════════════════════
# DIMENSI 2: 3T vs UMUM
# ═══════════════════════════════════════════════════════════════════════

# Kata kunci umum yang mengindikasikan daerah 3T
KEYWORDS_3T = [
    "3T", "terdepan", "terluar", "tertinggal",
    "daerah terpencil", "pedalaman", "pulau kecil", "pulau terluar",
    "perbatasan", "daerah tertinggal",
    "sulit dijangkau", "akses terbatas", "tidak ada sinyal",
    "desa terpencil", "pelosok",
]

# Daftar kabupaten 3T (sampel — bisa ditambah dari data Kemendes)
KABUPATEN_3T_SAMPLE = [
    # Papua
    "Pegunungan Bintang", "Yahukimo", "Nduga", "Lanny Jaya",
    "Mamberamo Raya", "Intan Jaya", "Puncak", "Puncak Jaya",
    "Tolikara", "Yalimo", "Deiyai", "Dogiyai",
    # NTT
    "Sumba Barat Daya", "Sumba Tengah", "Sabu Raijua",
    "Timor Tengah Selatan", "Manggarai Timur", "Alor",
    # Maluku
    "Maluku Barat Daya", "Kepulauan Aru", "Maluku Tenggara Barat",
    "Seram Bagian Barat", "Buru Selatan",
    # Kalimantan
    "Mahakam Ulu", "Kapuas Hulu", "Sintang",
    "Nunukan", "Malinau",
    # Sulawesi
    "Banggai Laut", "Morowali Utara",
    "Bolaang Mongondow Selatan",
    # Sumatera
    "Nias Selatan", "Nias Barat", "Kepulauan Mentawai",
]

# ═══════════════════════════════════════════════════════════════════════
# DIMENSI 3: LAYANAN UMUM (OFFLINE) vs DIGITAL
# ═══════════════════════════════════════════════════════════════════════

DIGITAL_KEYWORDS = [
    # Platform digital
    "online", "aplikasi", "website", "portal",
    "e-government", "e-service", "digital",
    "login", "registrasi online", "daftar online",
    # Aplikasi spesifik
    "mobile JKN", "JKN mobile", "BPJS online",
    "DJP online", "e-filing", "e-billing", "coretax",
    "SIGNAL", "SIM online", "e-KTP",
    "LAPOR!", "lapor.go.id",
    "SATU SEHAT", "satusehat",
    "OSS", "online single submission",
    "PPDB online", "e-PPDB",
    # Masalah digital
    "server down", "error", "loading", "crash",
    "tidak bisa login", "OTP tidak masuk",
    "verifikasi online gagal", "timeout",
    "aplikasi lemot", "bug", "maintenance",
]

UMUM_OFFLINE_KEYWORDS = [
    # Tempat fisik
    "kantor", "loket", "antri", "antrean",
    "datang langsung", "tatap muka",
    "fotokopi", "legalisir", "cap stempel",
    # Proses manual
    "formulir", "isi formulir", "blanko",
    "surat keterangan", "berkas fisik",
    "verifikasi manual", "tanda tangan basah",
    "bolak-balik", "pulang pergi",
    "bawa dokumen asli", "foto 3x4",
]

# ═══════════════════════════════════════════════════════════════════════
# PAIN POINT PATTERNS
# ═══════════════════════════════════════════════════════════════════════

PAIN_POINT_PATTERNS = {
    "data_tidak_valid": {
        "name": "Data Tidak Valid / Tidak Sinkron",
        "icon": "❌",
        "patterns": [
            "data tidak sesuai", "data tidak cocok", "data berbeda",
            "NIK salah", "NIK tidak ditemukan", "NIK tidak terdaftar",
            "data ganda", "data duplikat", "double data",
            "data tidak sinkron", "data tidak terintegrasi",
            "data tidak update", "data lama", "data usang",
            "nama salah", "tanggal lahir salah", "alamat tidak sesuai",
            "KK tidak sesuai", "KTP berbeda dengan",
        ],
    },
    "verifikasi_berulang": {
        "name": "Verifikasi Manual Berulang",
        "icon": "⏳",
        "patterns": [
            "verifikasi manual", "cek ulang", "konfirmasi lagi",
            "fotokopi berulang", "isi ulang formulir",
            "diminta ulang", "harus verifikasi lagi",
            "validasi ulang", "cek data lagi",
            "suruh datang lagi", "disuruh balik lagi",
        ],
    },
    "bolak_balik_instansi": {
        "name": "Bolak-balik Antar Instansi",
        "icon": "🔄",
        "patterns": [
            "bolak-balik", "bolak balik", "pulang pergi",
            "ke kantor lagi", "antar instansi",
            "lempar sana sini", "dilempar", "disuruh ke",
            "harus ke kelurahan dulu", "harus ke kecamatan dulu",
            "harus ke disdukcapil", "dari satu kantor ke kantor",
            "berkali-kali datang", "mondar-mandir",
        ],
    },
    "persyaratan_berlebihan": {
        "name": "Persyaratan Dokumen Berlebihan",
        "icon": "📋",
        "patterns": [
            "banyak syarat", "syarat ribet", "syarat berbelit",
            "dokumen kurang", "kurang dokumen",
            "fotokopi KTP", "fotokopi KK", "legalisir",
            "surat keterangan", "surat pengantar",
            "persyaratan banyak", "berkas banyak",
            "harus bawa", "diminta bawa",
        ],
    },
    "sistem_digital_gagal": {
        "name": "Sistem Digital Tidak Berfungsi",
        "icon": "💻",
        "patterns": [
            "error", "server down", "tidak bisa diakses",
            "loading terus", "timeout", "gagal login",
            "aplikasi crash", "aplikasi tidak bisa dibuka",
            "OTP tidak masuk", "verifikasi gagal",
            "sistem maintenance", "sedang perbaikan",
            "website error", "portal down",
            "data tidak muncul di aplikasi",
        ],
    },
    "salah_sasaran": {
        "name": "Salah Sasaran Penerima Manfaat",
        "icon": "🎯",
        "patterns": [
            "salah sasaran", "tidak tepat sasaran",
            "yang mampu dapat", "yang miskin tidak dapat",
            "seharusnya dapat", "tidak terdaftar padahal",
            "orang kaya dapat bansos", "yang berhak tidak dapat",
            "data penerima tidak akurat", "inclusion error",
            "exclusion error",
        ],
    },
}

# ═══════════════════════════════════════════════════════════════════════
# KELOMPOK DEMOGRAFIS TERDAMPAK
# ═══════════════════════════════════════════════════════════════════════

DEMOGRAPHIC_GROUPS = {
    "lansia": {
        "name": "Lansia",
        "icon": "👴",
        "patterns": [
            "orang tua", "lansia", "kakek", "nenek",
            "manula", "lanjut usia", "jompo",
            "usia lanjut", "usia tua",
        ],
    },
    "disabilitas": {
        "name": "Disabilitas",
        "icon": "♿",
        "patterns": [
            "disabilitas", "penyandang disabilitas",
            "cacat", "difabel",
            "tuna netra", "tuna rungu", "tuna daksa",
            "berkebutuhan khusus", "kursi roda",
        ],
    },
    "masyarakat_3t": {
        "name": "Masyarakat 3T",
        "icon": "🏔️",
        "patterns": [
            "masyarakat 3T", "daerah 3T",
            "pedalaman", "terpencil", "pulau kecil",
            "daerah terluar", "perbatasan",
            "sulit dijangkau", "tidak ada akses",
            "desa terpencil", "pelosok",
        ],
    },
    "ibu_anak": {
        "name": "Ibu dan Anak",
        "icon": "👩‍👧",
        "patterns": [
            "ibu hamil", "ibu melahirkan", "balita",
            "anak", "bayi", "stunting",
            "posyandu", "imunisasi anak",
            "akte kelahiran", "akta kelahiran",
        ],
    },
    "pekerja_informal": {
        "name": "Pekerja Informal",
        "icon": "💼",
        "patterns": [
            "buruh", "pekerja lepas", "pekerja harian",
            "ojol", "ojek online", "ojek",
            "pedagang kaki lima", "PKL",
            "pekerja informal", "freelance",
            "tidak punya slip gaji", "tanpa kontrak",
        ],
    },
    "petani_nelayan": {
        "name": "Petani dan Nelayan",
        "icon": "🌾",
        "patterns": [
            "petani", "nelayan", "pekebun",
            "buruh tani", "petani kecil",
            "nelayan kecil", "nelayan tradisional",
            "kartu tani", "asuransi nelayan",
        ],
    },
}

# ═══════════════════════════════════════════════════════════════════════
# PETA PROVINSI (untuk klasifikasi regional)
# ═══════════════════════════════════════════════════════════════════════

PROVINCES = [
    "Aceh", "Sumatera Utara", "Sumatera Barat", "Riau",
    "Jambi", "Sumatera Selatan", "Bengkulu", "Lampung",
    "Kepulauan Bangka Belitung", "Kepulauan Riau",
    "DKI Jakarta", "Jawa Barat", "Jawa Tengah",
    "DI Yogyakarta", "Jawa Timur", "Banten",
    "Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur",
    "Kalimantan Barat", "Kalimantan Tengah", "Kalimantan Selatan",
    "Kalimantan Timur", "Kalimantan Utara",
    "Sulawesi Utara", "Sulawesi Tengah", "Sulawesi Selatan",
    "Sulawesi Tenggara", "Gorontalo", "Sulawesi Barat",
    "Maluku", "Maluku Utara",
    "Papua", "Papua Barat", "Papua Selatan",
    "Papua Tengah", "Papua Pegunungan", "Papua Barat Daya",
]

# Alias umum untuk provinsi
PROVINCE_ALIASES = {
    "jakarta": "DKI Jakarta",
    "jabar": "Jawa Barat",
    "jateng": "Jawa Tengah",
    "jatim": "Jawa Timur",
    "jogja": "DI Yogyakarta",
    "yogya": "DI Yogyakarta",
    "sumut": "Sumatera Utara",
    "sumbar": "Sumatera Barat",
    "sumsel": "Sumatera Selatan",
    "babel": "Kepulauan Bangka Belitung",
    "kepri": "Kepulauan Riau",
    "kalbar": "Kalimantan Barat",
    "kalteng": "Kalimantan Tengah",
    "kalsel": "Kalimantan Selatan",
    "kaltim": "Kalimantan Timur",
    "kaltara": "Kalimantan Utara",
    "sulut": "Sulawesi Utara",
    "sulteng": "Sulawesi Tengah",
    "sulsel": "Sulawesi Selatan",
    "sultra": "Sulawesi Tenggara",
    "sulbar": "Sulawesi Barat",
    "malut": "Maluku Utara",
    "ntb": "Nusa Tenggara Barat",
    "ntt": "Nusa Tenggara Timur",
    "papbar": "Papua Barat",
}

# ═══════════════════════════════════════════════════════════════════════
# SINYAL ABANDONMENT (warga "malas menggunakan" layanan)
# ═══════════════════════════════════════════════════════════════════════

ABANDONMENT_SIGNALS = [
    "malas", "kapok", "males", "ogah",
    "menyerah", "nyerah", "pasrah",
    "tidak jadi", "batal", "urung",
    "tunda", "ditunda", "nanti saja",
    "ribet", "repot", "merepotkan",
    "susah", "sulit banget",
    "lebih baik tidak usah", "percuma",
    "sia-sia", "buang waktu", "buang-buang waktu",
    "frustrasi", "frustasi", "kesal",
    "kecewa", "mengecewakan",
    "trauma mengurus", "kapok ngurus",
]

# ═══════════════════════════════════════════════════════════════════════
# BOTTLENECK / WAKTU TERBUANG
# ═══════════════════════════════════════════════════════════════════════

BOTTLENECK_PATTERNS = [
    "berhari-hari", "berminggu-minggu", "berbulan-bulan",
    "berkali-kali", "puluhan kali", "belasan kali",
    "dari pagi sampai sore", "seharian",
    "antri berjam-jam", "antri panjang",
    "menunggu lama", "tunggu berminggu",
    "proses lama", "lambat",
    "belum selesai", "belum jadi",
    "tidak ada kepastian", "tidak jelas kapan",
]
