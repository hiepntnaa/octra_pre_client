#!/bin/bash

while true; do
    # Lấy ngẫu nhiên một dòng từ send.txt (wallet)
    wallet=$(shuf -n 1 send.txt)

    # In lệnh để kiểm tra
    echo "[$(date)] Running: python3 $wallet"

    # Thực thi lệnh
    python3 "$wallet"

    # Sinh thời gian ngủ ngẫu nhiên từ 10800 (180 phút) đến 12600 (210 phút) giây
    sleep_time=$((RANDOM % 1801 + 10800)) 
    echo "[$(date)] Sleeping for $sleep_time seconds (~$((sleep_time / 60)) minutes)..."
    sleep "$sleep_time"
done
