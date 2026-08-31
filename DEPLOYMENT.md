# 🌐 Panduan Hosting & Deployment Pipeline

Pipeline ini dapat di-host di cloud sehingga berjalan otomatis secara rutin tanpa memerlukan laptop menyala.

---

## Opsi 1: GitHub Actions (Paling Praktis & 100% GRATIS) ⭐

Jika kode Anda disimpan di GitHub (Private maupun Public Repo):

1. **Push kode ke GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/USERNAME/REPO.git
   git push -u origin main
   ```
2. Workflow telah disiapkan di [`.github/workflows/scheduled_pipeline.yml`](.github/workflows/scheduled_pipeline.yml).
3. **Jadwal Otomatis**: Pipeline akan berjalan setiap hari pada pukul **07:00 WIB (00:00 UTC)**.
4. **Download Hasil**: Buka tab **Actions** di GitHub ➔ klik eksekusi workflow terbaru ➔ unduh file zip laporan pada bagian **Artifacts**.
5. **(Opsional) API Keys**: Jika punya API key Reddit/YouTube, tambahkan di **Settings ➔ Secrets and variables ➔ Actions**.

---

## Opsi 2: Cloud VPS (DigitalOcean / Hetzner / AWS Lightsail)

VPS Linux ($4 - $5/bulan) memberikan kebebasan penuh untuk scraping data skala besar.

### Langkah Setup di VPS (Ubuntu):
1. **Login ke VPS**:
   ```bash
   ssh root@IP_VPS_ANDA
   ```
2. **Clone & Install**:
   ```bash
   git clone https://github.com/USERNAME/REPO.git antah
   cd antah
   apt update && apt install -y python3-pip python3-venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Jalankan Background 24/7**:
   ```bash
   nohup python3 -u run_pipeline.py --days 365 > logs/pipeline.log 2>&1 &
   ```
4. **Jadwalkan Rutin via Crontab**:
   Ketik `crontab -e` lalu tambahkan baris berikut agar jalan otomatis tiap jam 02.00 pagi:
   ```cron
   0 2 * * * cd /root/antah && /root/antah/venv/bin/python run_pipeline.py --days 7 >> /root/antah/logs/cron.log 2>&1
   ```

---

## Opsi 3: Railway / Render (PaaS)

1. Hubungkan repository GitHub ke **Railway.app** atau **Render.com**.
2. Platform akan otomatis mendeteksi [`Dockerfile`](Dockerfile).
3. Buat cron job / background worker sesuai kebutuhan melalui dashboard mereka.
