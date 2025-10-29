# UPI Transaction Analysis — Neha Gadge

Interactive Streamlit dashboard analyzing UPI transactions dataset.

## Features
- Upload Excel (UPI+Transactions.xlsx) or use built-in file under data/
- Monthly trend of total transaction amounts
- Payment method and transaction-type breakdowns
- Top merchants by total amount
- Scatter plots, trendlines and optional heatmap by hour/weekdays
- Filters: date range, city, payment method, status, amount range
- Download filtered dataset as CSV

## Files
- app.py — Streamlit app (main)
- requirements.txt — Python dependencies
- data/UPI+Transactions.xlsx — place your dataset here (or use file uploader in-app)

## Run locally
1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate      # Windows
