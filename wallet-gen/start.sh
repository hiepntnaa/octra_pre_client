#!/bin/bash

# Function to install Bun
install_bun() {
    echo "Installing Bun..."
    if command -v bun &> /dev/null; then
        echo "Bun is already installed. Version: $(bun --version)"
    else
        echo "Installing Bun..."
        curl -fsSL https://bun.sh/install | bash
        # Set PATH to include Bun's binary directory
        export PATH="$HOME/.bun/bin:$PATH"
        echo "Bun installed successfully!"
    fi
}

# Build from source
echo "=== Building from Source ==="

# Install Bun if not present
install_bun

echo ""
echo "Installing dependencies..."
bun install

echo ""
echo "Building standalone executable..."
bun run build

if [ ! -f "./wallet-generator" ]; then
    echo "❌ Error: wallet-generator executable not found!"
    echo "Build may have failed. Please check the build output above."
    exit 1
fi

echo ""
echo "Build complete!"
echo ""

# Execute binary
echo "=== Starting Wallet Generator ==="
echo ""
echo "Starting wallet generator server..."

# Start the binary in the background
./wallet-generator &
WALLET_PID=$!

# Wait a moment for the server to start
sleep 5

# Open browser

echo "=== OCTRA Wallet Generator ==="

# Đường dẫn file cấu hình ngrok
NGROK_CONFIG_FILE="$HOME/.config/ngrok/ngrok.yml"

# Kiểm tra và cấu hình ngrok nếu chưa có
if [ -f "$NGROK_CONFIG_FILE" ]; then
else
    read -p "Nhap ngrok token cua ban: " NGROK_TOKEN
    if [ -n "$NGROK_TOKEN" ]; then
        ngrok config add-authtoken "$NGROK_TOKEN"
    else
        echo "Khong nhap token. Thoat."
        exit 1
    fi
fi


# Kiểm tra nếu ngrok chưa chạy
if ! curl -s http://127.0.0.1:4040/api/tunnels &> /dev/null; then
    echo "Dang khoi dong ngrok tunnel..."
    nohup ngrok http 8888 > /dev/null 2>&1 &
    sleep 5
else
    echo "Phat hien ngrok tunnel dang chay, lay URL hien tai..."
fi

# Lấy URL từ ngrok
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | jq -r '.tunnels[0].public_url')

if [[ -n "$NGROK_URL" && "$NGROK_URL" == https://* ]]; then
    echo "Ngrok dang chay tai: $NGROK_URL"
else
    echo "Khong the lay URL tu ngrok. Kiem tra lai cau hinh hoac port 8888."
fi

# Wait for the background process
wait $WALLET_PID 
