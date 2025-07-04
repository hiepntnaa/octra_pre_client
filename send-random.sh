#!/bin/bash

while true; do
    # Lấy ngẫu nhiên một dòng từ send.txt (wallet)
    wallet=$(shuf -n 1 send.txt)

    # Lấy ngẫu nhiên một dòng từ addr.txt (địa chỉ nhận)
    addr=$(shuf -n 1 addr.txt)

    # Sinh số ngẫu nhiên từ 0.001 đến 0.009 với 3 chữ số thập phân
    vol=$(awk -v min=0.001 -v max=0.009 'BEGIN{srand(); printf "%.3f", min + rand() * (max - min)}')

    # In lệnh để kiểm tra
    echo "[$(date)] Running: python3 $wallet $addr $vol"

    # Thực thi lệnh
    python3 "$wallet" "$addr" "$vol"

    # Sinh thời gian ngủ ngẫu nhiên từ 900 (15 phút) đến 1500 (25 phút) giây
    sleep_time=$((RANDOM % 601 + 900))  # 900 + [0–600] = 900–1500
    echo "[$(date)] Sleeping for $sleep_time seconds (~$((sleep_time / 60)) minutes)..."
    sleep "$sleep_time"
done
