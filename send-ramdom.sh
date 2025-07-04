#!/bin/bash

# Lấy ngẫu nhiên một dòng từ send.txt (wallet)
wallet=$(shuf -n 1 send.txt)

# Lấy ngẫu nhiên một dòng từ send-addr.txt (địa chỉ nhận)
send_addr=$(shuf -n 1 send-addr.txt)

# Sinh số ngẫu nhiên từ 0.001 đến 0.009 với 3 chữ số thập phân
random_vol=$(awk -v min=0.001 -v max=0.009 'BEGIN{srand(); printf "%.3f", min + rand() * (max - min)}')

# In lệnh để kiểm tra (bạn có thể bỏ dòng echo này nếu không cần)
echo "python3 $wallet $send_addr $random_vol"

# Thực thi lệnh
python3 "$wallet" "$send_addr" "$random_vol"
