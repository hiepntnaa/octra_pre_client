#!/bin/bash

# Hỏi người dùng muốn tạo bao nhiêu ví
read -p "Bạn muốn tạo bao nhiêu ví? " NUM_WALLETS

# Kiểm tra đầu vào có phải là số không
if ! [[ "$NUM_WALLETS" =~ ^[0-9]+$ ]]; then
    echo "❌ Vui lòng nhập một số nguyên hợp lệ."
    exit 1
fi

# Tên file kết quả
OUTPUT_FILE="wallets_output.txt"

# Xóa file cũ nếu tồn tại
> "$OUTPUT_FILE"

echo "������ Đang tạo $NUM_WALLETS ví..."

# Vòng lặp tạo ví
for ((i=1; i<=NUM_WALLETS; i++)); do
    echo "Ví $i:" >> "$OUTPUT_FILE"
    bun wallet_generator.ts generate >> "$OUTPUT_FILE"
    echo -e "\n" >> "$OUTPUT_FILE"
done

echo "✅ Đã tạo $NUM_WALLETS ví. Kết quả lưu trong: $OUTPUT_FILE"
