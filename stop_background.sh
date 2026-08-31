#!/bin/bash
# ==============================================================================
# Script untuk menghentikan Pipeline yang sedang berjalan di background
# ==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

PID_FILE="logs/pipeline.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "ℹ️ Tidak ada PID file. Mencari proses pipeline secara manual..."
    pkill -f "run_pipeline.py"
    pkill -f "run_scrape.py"
    pkill -f "run_analyze.py"
    echo "✅ Selesai."
    exit 0
fi

PID=$(cat "$PID_FILE")
if ps -p "$PID" > /dev/null 2>&1; then
    echo "🛑 Menghentikan proses pipeline (PID: $PID)..."
    kill "$PID" 2>/dev/null
    sleep 2
    if ps -p "$PID" > /dev/null 2>&1; then
        kill -9 "$PID" 2>/dev/null
    fi
    pkill -f "run_scrape.py" 2>/dev/null
    pkill -f "run_analyze.py" 2>/dev/null
    rm -f "$PID_FILE"
    echo "✅ Pipeline berhasil dihentikan."
else
    echo "ℹ️ Proses dengan PID $PID sudah tidak aktif."
    rm -f "$PID_FILE"
fi
