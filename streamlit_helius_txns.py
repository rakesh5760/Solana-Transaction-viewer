# streamlit_helius_txns.py
"""
Streamlit frontend for fetching Solana transactions via Helius.

How to run:
  pip install streamlit requests pandas
  # Option A: set HELIUS_API_KEY in your environment (recommended)
  # Windows PowerShell:
  # $env:HELIUS_API_KEY = "your_key_here"
  streamlit run streamlit_helius_txns.py
"""

from typing import Optional, List, Dict, Any
import time
import json
import requests
from datetime import datetime
import pandas as pd
import streamlit as st
import os

HELIUS_BASE = "https://api.helius.xyz/v0/addresses"

st.set_page_config(page_title="Helius — Solana Txns Viewer", layout="wide")
st.title("Helius — Solana Transactions Viewer")

# --- helpers ---
def epoch_to_iso(ts: Optional[int]) -> Optional[str]:
    if ts is None:
        return None
    try:
        return datetime.utcfromtimestamp(int(ts)).isoformat() + "Z"
    except Exception:
        return None

def helius_fetch_page(address: str, api_key: str, limit: int = 100, cursor: Optional[str] = None) -> Dict[str, Any]:
    url = f"{HELIUS_BASE}/{address}/transactions"
    params = {"limit": limit, "api-key": api_key}
    if cursor:
        params["cursor"] = cursor
    headers = {"Accept": "application/json", "api-key": api_key}
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def collect_pages(address: str, api_key: str, limit: int, max_pages: int) -> (List[Dict[str, Any]], Optional[str], int):
    """
    Collect pages from Helius. Returns (collected_items, last_cursor, pages_fetched)
    """
    collected = []
    cursor = None
    pages = 0
    while True:
        if max_pages and pages >= max_pages:
            break
        pages += 1
        data = helius_fetch_page(address, api_key, limit=limit, cursor=cursor)
        # normalize tx list and next cursor
        txs = None
        next_cursor = None
        if isinstance(data, dict):
            if isinstance(data.get("transactions"), list):
                txs = data["transactions"]
            elif isinstance(data.get("result"), list):
                txs = data["result"]
            else:
                for v in data.values():
                    if isinstance(v, list):
                        txs = v
                        break
            for k in ("cursor", "next", "nextCursor", "next_cursor"):
                if k in data and data[k]:
                    next_cursor = data[k]
                    break
        elif isinstance(data, list):
            txs = data

        if not txs:
            break

        collected.extend(txs)
        # if no next, break
        if not next_cursor:
            cursor = None
            break
        cursor = next_cursor
        # polite pause
        time.sleep(0.12)
    return collected, cursor, pages

def flatten_summary(transactions: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for tx in transactions:
        sig = tx.get("signature") or tx.get("txHash") or tx.get("transactionHash")
        slot = tx.get("slot")
        ts = tx.get("timestamp") or tx.get("blockTime") or tx.get("block_time")
        fee_lam = tx.get("fee") or 0
        fee_sol = fee_lam / 1e9 if isinstance(fee_lam, (int, float)) else None
        fee_payer = tx.get("feePayer")
        native_cnt = len(tx.get("nativeTransfers") or [])
        token_cnt = len(tx.get("tokenTransfers") or [])
        err = tx.get("transactionError")
        description = tx.get("description") or tx.get("type") or ""
        rows.append({
            "signature": sig,
            "slot": slot,
            "time_utc": epoch_to_iso(ts),
            "timestamp": ts,
            "fee_lamports": fee_lam,
            "fee_sol": fee_sol,
            "feePayer": fee_payer,
            "nativeTransfers": native_cnt,
            "tokenTransfers": token_cnt,
            "error": json.dumps(err) if err else None,
            "description": description
        })
    df = pd.DataFrame(rows)
    return df

# --- UI inputs ---
with st.sidebar:
    st.header("Settings")
    # prefer env var
    env_key = os.environ.get("HELIUS_API_KEY")
    use_env = False
    if env_key:
        use_env = st.checkbox("Use HELIUS_API_KEY from environment", value=True)
    helius_key_input = None
    if not use_env:
        helius_key_input = st.text_input("Helius API Key (masked)", type="password")
    helius_key = env_key if (env_key and use_env) else helius_key_input

    st.markdown("---")
    st.subheader("Fetch options")
    limit = st.number_input("Limit per page", min_value=1, max_value=500, value=100, step=10)
    max_pages = st.number_input("Max pages (0 = unlimited)", min_value=0, max_value=100, value=1, step=1)
    st.markdown("**Note:** keep max_pages small while testing to avoid rate limits.")

# main inputs
col1, col2 = st.columns([3,1])
with col1:
    address = st.text_input("Solana wallet address", placeholder="Enter public address here")
with col2:
    fetch_btn = st.button("Fetch transactions")

st.markdown("---")

if fetch_btn:
    if not address:
        st.error("Enter a Solana address first.")
    elif not helius_key:
        st.error("Provide a Helius API key (via env or input).")
    else:
        status = st.empty()
        status.info("Collecting transactions from Helius...")
        progress = st.progress(0)
        try:
            txs, last_cursor, pages = collect_pages(address.strip(), helius_key.strip(), limit=int(limit), max_pages=int(max_pages))
            status.success(f"Fetched {len(txs)} transactions (pages fetched: {pages}).")
            progress.progress(100)

            # show summary dataframe
            if txs:
                df = flatten_summary(txs)
                st.subheader("Summary table")
                st.dataframe(df, use_container_width=True)

                # download buttons
                json_bytes = json.dumps(txs, indent=2).encode("utf-8")
                st.download_button("Download raw JSON", data=json_bytes, file_name=f"helius_{address}_txns.json", mime="application/json")

                csv_bytes = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download summary CSV", data=csv_bytes, file_name=f"helius_{address}_summary.csv", mime="text/csv")

                # expand a selected tx
                st.subheader("Select transaction to inspect")
                sigs = df["signature"].tolist()
                sel = st.selectbox("Pick signature", options=sigs)
                if sel:
                    tx_obj = next((t for t in txs if (t.get("signature") == sel or t.get("txHash") == sel)), None)
                    if tx_obj:
                        st.json(tx_obj)
            else:
                st.warning("No transactions returned by Helius for this address / page range.")
        except requests.HTTPError as e:
            status.error(f"HTTP error: {e}")
        except Exception as e:
            status.error(f"Error: {e}")
