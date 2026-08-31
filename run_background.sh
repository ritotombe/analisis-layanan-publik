#!/bin/bash
# ==============================================================================
# Script untuk menjalankan Pipeline di Background (Offline / Laptop Ditutup)
# Menggunakan caffeinate (macOS) + nohup agar proses tidak mati saat layar mati
# ==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

mkdir -p logs output data/exports

LOG_FILE="logs/pipeline_background.log"
PID_FILE="logs/pipeline.pid"

# Cek apakah sudah ada proses yang berjalan
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️ Pipeline sudah berjalan di background (PID: $PID)."
        echo "   Pantau log: tail -f $LOG_FILE"
        echo "   Hentikan:   ./stop_background.sh"
        exit 1
    fi
fi

ARGS="${@:---days 365}"

echo "============================================================"
echo "🚀 Menjalankan Pipeline di Background"
echo "============================================================"
echo "📁 Direktori: $DIR"
echo "📄 Log Output: $LOG_FILE"
echo "⚙️ Parameter:  $ARGS"
echo "💤 Proteksi:   caffeinate aktif (tetap jalan saat laptop tidur/layar mati)"
echo "============================================================"

# Jalankan dengan caffeinate (mencegah sleep di macOS) dan nohup
nohup caffeinate -s -i python3 -u run_pipeline.py $ARGS > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"

echo "✅ Pipeline berhasil dijalankan di background (PID: $PID)"
echo ""
echo "Perintah berguna:"
echo "  • Pantau progres:   python3 check_status.py"
echo "  • Lihat live log:   tail -f $LOG_FILE"
echo "  • Hentikan proses:  ./stop_background.sh"
echo "============================================================"
