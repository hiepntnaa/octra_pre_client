#!/bin/bash

if [ -z "$1" ]; then
    read -p "Nhap so vi can tao: " COUNT
else
    COUNT=$1
fi

# File CSV đầu ra
OUTPUT_FILE="wallets_summary.csv"

# Ghi tiêu đề cột, dùng dấu chấm phẩy
echo "Wallet;Mnemonic;PrivateKey;PublicKey;Address" > "$OUTPUT_FILE"

# Vòng lặp tạo ví
for ((i=1; i<=COUNT; i++)); do
    echo "Dang tao vi $i..."

    OUTPUT=$(bun wallet_generator.ts generate)

    MNEMONIC=$(echo "$OUTPUT" | grep -i "^Mnemonic:" | cut -d':' -f2- | xargs)
    PRIVKEY=$(echo "$OUTPUT" | grep -i "^Private Key" | cut -d':' -f2- | xargs)
    PUBKEY=$(echo "$OUTPUT" | grep -i "^Public Key" | cut -d':' -f2- | xargs)
    ADDRESS=$(echo "$OUTPUT" | grep -i "^Address:" | cut -d':' -f2- | xargs)

    # Escape dấu nháy kép nếu có
    MNEMONIC_ESCAPED=$(echo "$MNEMONIC" | sed 's/"/""/g')

    # Ghi dòng với dấu chấm phẩy
    echo "\"Wallet $i\";\"$MNEMONIC_ESCAPED\";\"$PRIVKEY\";\"$PUBKEY\";\"$ADDRESS\"" >> "$OUTPUT_FILE"
done

echo "Da tao $COUNT vi va luu vao '$OUTPUT_FILE'"
