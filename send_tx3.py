#!/usr/bin/env python3
"""
Octra Direct Transaction Sender
Usage: python send_tx.py <to_address> <amount> [message]
"""
import json
import base64
import hashlib
import time
import sys
import re
import random
import asyncio
import aiohttp
import nacl.signing
from datetime import datetime

# Constants
μ = 1_000_000
b58 = re.compile(r"^oct[1-9A-HJ-NP-Za-km-z]{44}$")

# Global variables
priv = None
addr = None
rpc = None
sk = None
pub = None
session = None

def load_wallet():
    """Load wallet configuration from wallet3.json"""
    global priv, addr, rpc, sk, pub
    try:
        with open('wallet3.json', 'r') as f:
            data = json.load(f)
        priv = data.get('priv')
        addr = data.get('addr')
        rpc = data.get('rpc', 'https://octra.network')
        sk = nacl.signing.SigningKey(base64.b64decode(priv))
        pub = base64.b64encode(sk.verify_key.encode()).decode()
        return True
    except Exception as e:
        print(f"Error loading wallet: {e}")
        return False

async def request(method, path, data=None, timeout=10):
    """Make HTTP request to the RPC server"""
    global session
    if not session:
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout))
    
    try:
        url = f"{rpc}{path}"
        if method.upper() == 'POST':
            async with session.post(url, json=data) as resp:
                text = await resp.text()
        else:
            async with session.get(url, json=data) as resp:
                text = await resp.text()
        
        try:
            json_data = json.loads(text) if text else None
        except:
            json_data = None
        
        return resp.status, text, json_data
    except Exception as e:
        return 0, str(e), None

async def get_balance_and_nonce():
    """Get current balance and nonce for the address"""
    # Get balance and nonce
    status, text, json_data = await request('GET', f'/balance/{addr}')
    
    if status == 200 and json_data:
        nonce = int(json_data.get('nonce', 0))
        balance = float(json_data.get('balance', 0))
        
        # Check staging for pending transactions to adjust nonce
        status2, _, json_data2 = await request('GET', '/staging', 5)
        if status2 == 200 and json_data2:
            our_txs = [tx for tx in json_data2.get('staged_transactions', []) if tx.get('from') == addr]
            if our_txs:
                nonce = max(nonce, max(int(tx.get('nonce', 0)) for tx in our_txs))
        
        return nonce, balance
    elif status == 404:
        return 0, 0.0
    elif status == 200 and text and not json_data:
        # Try to parse plain text response
        try:
            parts = text.strip().split()
            if len(parts) >= 2:
                balance = float(parts[0]) if parts[0].replace('.', '').isdigit() else 0.0
                nonce = int(parts[1]) if parts[1].isdigit() else 0
                return nonce, balance
        except:
            pass
    
    return None, None

def create_transaction(to_address, amount, nonce, message=None):
    """Create and sign a transaction"""
    tx = {
        "from": addr,
        "to_": to_address,
        "amount": str(int(amount * μ)),
        "nonce": int(nonce),
        "ou": "1" if amount < 1000 else "3",
        "timestamp": time.time() + random.random() * 0.01
    }
    
    if message:
        tx["message"] = message
    
    # Create signature payload (without message field)
    sig_data = {k: v for k, v in tx.items() if k != "message"}
    sig_payload = json.dumps(sig_data, separators=(",", ":"))
    
    # Sign the transaction
    signature = base64.b64encode(sk.sign(sig_payload.encode()).signature).decode()
    
    # Add signature and public key to transaction
    tx.update(signature=signature, public_key=pub)
    
    # Calculate transaction hash
    tx_hash = hashlib.sha256(sig_payload.encode()).hexdigest()
    
    return tx, tx_hash

async def send_transaction(tx):
    """Send transaction to the network"""
    start_time = time.time()
    status, text, json_data = await request('POST', '/send-tx', tx)
    duration = time.time() - start_time
    
    if status == 200:
        if json_data and json_data.get('status') == 'accepted':
            return True, json_data.get('tx_hash', ''), duration, json_data
        elif text.lower().startswith('ok'):
            return True, text.split()[-1], duration, None
    
    error_msg = json.dumps(json_data) if json_data else text
    return False, error_msg, duration, json_data

async def main():
    global session
    
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Usage: python send_tx.py <to_address> <amount> [message]")
        print("Example: python send_tx.py oct1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q8R9S0T 10.5 'Hello World'")
        sys.exit(1)
    
    to_address = sys.argv[1]
    try:
        amount = float(sys.argv[2])
    except ValueError:
        print("Error: Amount must be a valid number")
        sys.exit(1)
    
    message = sys.argv[3] if len(sys.argv) > 3 else None
    if message and len(message) > 1024:
        message = message[:1024]
        print("Warning: Message truncated to 1024 characters")
    
    # Validate inputs
    if not b58.match(to_address):
        print("Error: Invalid address format")
        sys.exit(1)
    
    if amount <= 0:
        print("Error: Amount must be greater than 0")
        sys.exit(1)
    
    # Load wallet
    if not load_wallet():
        print("Error: Could not load wallet3.json")
        sys.exit(1)
    
    print(f"Loaded wallet: {addr}")
    print(f"RPC endpoint: {rpc}")
    
    try:
        # Get current balance and nonce
        print("Getting balance and nonce...")
        nonce, balance = await get_balance_and_nonce()
        
        if nonce is None or balance is None:
            print("Error: Could not get balance and nonce")
            sys.exit(1)
        
        print(f"Current balance: {balance:.6f} OCT")
        print(f"Current nonce: {nonce}")
        
        # Check if we have sufficient balance
        if balance < amount:
            print(f"Error: Insufficient balance ({balance:.6f} < {amount})")
            sys.exit(1)
        
        # Create transaction
        print("Creating transaction...")
        tx, tx_hash = create_transaction(to_address, amount, nonce + 1, message)
        
        fee = 0.001 if amount < 1000 else 0.003
        print(f"Transaction details:")
        print(f"  To: {to_address}")
        print(f"  Amount: {amount:.6f} OCT")
        print(f"  Fee: {fee} OCT")
        print(f"  Nonce: {nonce + 1}")
        if message:
            print(f"  Message: {message}")
        
        # Send transaction
        print("Sending transaction...")
        success, result, duration, response = await send_transaction(tx)
        
        if success:
            print(f"✓ Transaction sent successfully!")
            print(f"  Hash: {result}")
            print(f"  Time: {duration:.2f}s")
            if response and 'pool_info' in response:
                pool_size = response['pool_info'].get('total_pool_size', 0)
                print(f"  Pool: {pool_size} transactions pending")
        else:
            print(f"✗ Transaction failed!")
            print(f"  Error: {result}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nTransaction cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        if session:
            await session.close()

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=ResourceWarning)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
