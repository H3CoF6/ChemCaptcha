#!/bin/bash
set -e

# !!!! rich !!!  TUI的编码问题！！
export PYTHONIOENCODING=utf-8
export TERM=xterm-256color
export FORCE_COLOR=true

echo "--- Starting Application Container ---"


echo "[1/3] Running scripts.docker_split in background (silent)..."
python -m scripts.docker_split > /dev/null 2>&1 &

echo "Waiting for split process to initialize..."
sleep 5

echo "[2/3] Running scripts.init_sqlite..."
python -m scripts.init_sqlite

echo "[3/3] Starting FastAPI server..."

exec python -m app.main