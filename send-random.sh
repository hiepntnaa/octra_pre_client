#!/bin/bash

while true; do
    # Lấy ngẫu nhiên một dòng từ send.txt (wallet)
    wallet=$(shuf -n 1 send.txt)

    # In lệnh để kiểm tra
    echo "[$(date)] Running: python3 $wallet"

    # Thực thi lệnh
    python3 "$wallet"

    # Sinh thời gian ngủ ngẫu nhiên từ 900 (15 phút) đến 1500 (25 phút) giây
    sleep_time=$((RANDOM % 601 + 900))  # 900 + [0–600] = 900–1500
    echo "[$(date)] Sleeping for $sleep_time seconds (~$((sleep_time / 60)) minutes)..."
    sleep "$sleep_time"
done
