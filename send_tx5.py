import asyncio
import random
from pathlib import Path

import cli5
from cli5 import (
    ld, st, mk, snd, μ,
    encrypt_balance, decrypt_balance,
    get_encrypted_balance, create_private_transfer,
    get_address_info, get_pending_transfers, claim_private_transfer
)

async def delay():
    seconds = random.randint(180, 240)
    print(f"[delay] Waiting for {seconds} seconds...\n")
    await asyncio.sleep(seconds)

async def send_tx(to_addr):
    n, balance = await st()
    if balance is None or n is None or balance < 0.001:
        print("[send] Insufficient balance.")
        return None

    amount = round(random.uniform(0.0010, 0.0200), 6)
    if amount > balance:
        print("[send] Skipping send due to insufficient balance.")
        return None

    tx, _ = mk(to_addr, amount, n + 1)
    ok, hash, _, _ = await snd(tx)
    if ok:
        print(f"[send] Sent {amount} OCT to {to_addr}, hash: {hash}")
        return amount
    else:
        print(f"[send] Failed to send.")
        return None

async def do_encrypt():
    amount = round(random.uniform(0.0010, 0.0200), 6)
    ok, result = await encrypt_balance(amount)
    if ok:
        print(f"[encrypt] Encrypted {amount} OCT")
        return amount
    else:
        print(f"[encrypt] Failed to encrypt. Reason: {result.get('error')}")
        return None

async def do_private_transfer(to_addr, max_amount):
    amount = round(random.uniform(0.0005, max(0.0005, max_amount)), 6)
    addr_info = await get_address_info(to_addr)
    if not addr_info or not addr_info.get("has_public_key"):
        print(f"[transfer] Recipient {to_addr} not ready for private transfers.")
        return amount

    ok, result = await create_private_transfer(to_addr, amount)
    if ok:
        print(f"[transfer] Sent private transfer {amount} OCT to {to_addr}")
    else:
        print(f"[transfer] Failed. Reason: {result.get('error')}")
    return amount

async def do_decrypt(max_amount):
    amount = round(random.uniform(0.0005, max_amount / 2), 6)

    for attempt in range(3):
        enc_data = await get_encrypted_balance()
        if enc_data is None:
            print(f"[decrypt] Attempt {attempt+1}/3: cannot get balance, retrying...")
            await asyncio.sleep(5)
            continue

        if enc_data["encrypted_raw"] / μ < amount:
            print(f"[decrypt] Skipping: encrypted balance too low ({enc_data['encrypted']:.6f} < {amount:.6f})")
            return

        ok, result = await decrypt_balance(amount)
        if ok:
            print(f"[decrypt] Decrypted {amount} OCT")
        else:
            print(f"[decrypt] Failed. Reason: {result.get('error')}")
        return

    print("[decrypt] Failed after 3 attempts: cannot get balance")

async def do_claim_transfers():
    # Đảm bảo session được khởi tạo nếu chưa có
    if not cli5.session:
        await cli5.req("GET", "/ping")  # tạo session giả
    
    await asyncio.sleep(5)  # đợi blockchain đồng bộ

    transfers = await get_pending_transfers()
    if not transfers:
        print("[claim] No transfers found.")
        return

    if len(transfers) <= 1:
        print(f"[claim] Skipping: only {len(transfers)} transfer(s) available.")
        return

    print(f"[claim] Found {len(transfers)} claimable transfers. Claiming now...")

    success = 0
    for t in transfers:
        transfer_id = t.get("id")
        if not transfer_id:
            continue
        ok, result = await claim_private_transfer(transfer_id)
        if ok:
            success += 1
            print(f"[claim] ✅ Claimed transfer #{transfer_id}")
        else:
            print(f"[claim] ✗ Failed to claim #{transfer_id}: {result.get('error')}")

    print(f"[claim] Done. Claimed {success}/{len(transfers)} transfers.")

async def run_once(to_addr):
    print(f"--- Starting single cycle for recipient: {to_addr} ---")

    await send_tx(to_addr)
    await delay()

    encrypt_amount = await do_encrypt()
    if not encrypt_amount:
        return
    await delay()

    transferred = await do_private_transfer(to_addr, encrypt_amount)
    await delay()

    await do_decrypt(encrypt_amount)
    await delay()

    await do_claim_transfers()

    print("✅ Cycle complete. Program ends.\n")

async def main():
    if not cli5.ld():
        print("[error] Failed to load wallet")
        return

    addr_list = Path("addr.txt").read_text().splitlines()
    addr_list = [a.strip() for a in addr_list if a.strip()]
    if not addr_list:
        print("[error] addr.txt is empty.")
        return

    to_addr = random.choice(addr_list)
    try:
        await run_once(to_addr)
    except Exception as e:
        print(f"[error] Exception occurred: {e}")
    finally:
        try:
            if cli5.session and not cli5.session.closed:
                await cli5.session.close()
        except Exception as e:
            print(f"[error] Failed to close session: {e}")

if __name__ == "__main__":
    asyncio.run(main())
