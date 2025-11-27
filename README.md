# Solana-Transaction-viewer
A complete Solana transaction explorer built with FastAPI + Streamlit. Fetches enriched transaction data using the Helius API and displays it in a clean dashboard with summaries, detailed views, and CSV/JSON exports. Supports pagination, dynamic wallet lookup, and real-time blockchain analysis.




# Solana Transactions Viewer (FastAPI + Streamlit + Helius)

A simple but powerful Solana transaction explorer built using:

- **Helius API** (enhanced Solana transaction indexing)
- **FastAPI** (backend API)
- **Streamlit** (frontend UI)
- **Python** (requests, pandas)

This tool allows you to enter **any Solana wallet address** and instantly view:

- Full transaction history via Helius
- Native SOL transfers
- Token transfers
- Fees, timestamps, slot numbers
- Expanded raw JSON per transaction
- Downloadable JSON & CSV
- Pagination support (limit, max_pages)

---

## 🚀 Features

### ✔ FastAPI Backend  
- Fetches Solana transactions from Helius  
- No date filtering (optional)  
- Supports cursor-based pagination  
- Clean JSON response  

### ✔ Streamlit Frontend  
- Enter wallet address dynamically  
- Enter Helius API key (or use environment variable)  
- Paginated transaction fetch  
- Summary table for each transaction  
- Expandable full JSON view  
- Download:
  - Raw JSON  
  - Flattened CSV  

---

## 📦 Installation

### 1. Install dependencies
```bash```
pip install -r requirements.txt



▶ Running the Project
1️⃣ Run the FastAPI backend (optional)

If you are using FastAPI for API access:

```bash```
uvicorn fastapi_helius_txns:app --reload --port 8000

Backend will be available at:

http://127.0.0.1:8000/txns/<address>


2️⃣ Run the Streamlit frontend
streamlit run streamlit_helius_txns.py


Streamlit UI will open in your browser:

http://localhost:8501




🗂 Project Structure
📦 project
 ┣ 📄 fastapi_helius_txns.py
 ┣ 📄 streamlit_helius_txns.py
 ┣ 📄 requirements.txt
 ┗ 📄 README.md



 🔑 API Keys

This project uses Helius API.

Get a free API key from:
👉 https://dev.helius.xyz/dashboard

You can supply the API key in two ways:

Set environment variable HELIUS_API_KEY

Enter it inside the Streamlit UI (masked input)

📁 Outputs

The Streamlit UI allows downloading:

1. Raw JSON

Exact transaction objects from Helius.

2. CSV Summary

A flattened table containing:
  signature
  
  slot
  
  timestamp
  
  SOL fee
  
  nativeTransfers count
  
  tokenTransfers count
  
  error
  
  description

🧪 Testing Addresses

You can test with these common Solana accounts:

Token Program:     TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA
System Program:    11111111111111111111111111111111
USDC Mint:         EPjFWdd5AufqSSqeM2qvZqB7yRGX5QwJWAzvKxGnhV9



📜 License

MIT — free to use, modify, or extend.

🙌 Contribution

Feel free to open issues or request enhancements such as:

Date-based transaction filtering

Token metadata lookup

SOL/USDC price integration

Faster async API calls

