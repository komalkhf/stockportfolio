import requests
import json
from google.cloud import bigquery, firestore, storage
from datetime import datetime, timedelta

# --- FINNHUB Config ---
FINNHUB_API_KEY = 'd0avurhr01qlq65q0280d0avurhr01qlq65q028g'
TICKERS = "SCHD,SCHG,NVDA,MSFT,LLY"
GCS_BUCKET = 'fpkkhawaja'

# --- GCP Clients ---
bq_client = bigquery.Client()
fs_client = firestore.Client()
gcs_client = storage.Client()

def fetch_and_store_stock_data(request):
    timestamp = datetime.utcnow().isoformat()
    tickers_list = TICKERS.split(',')

    # --- Stock Price Data Block ---
    try:
        for ticker in tickers_list:
            price_url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
            price_res = requests.get(price_url)
            price_data = price_res.json()

            stock_payload = {
                "symbol": ticker,
                "current_price": price_data.get("c"),
                "high_price": price_data.get("h"),
                "low_price": price_data.get("l"),
                "open_price": price_data.get("o"),
                "previous_close": price_data.get("pc"),
                "timestamp": timestamp,
                "volume": price_data.get("v")
            }

            bq_client.insert_rows_json(
                'sp25-i535-kkhawaja-portfolio.stock_data.stock_price',
                [stock_payload]
            )

            fs_client.collection('logs').add({
                "source": "stock_price",
                "status": "inserted",
                "data": stock_payload
            })

    except Exception as e:
        fs_client.collection('logs').add({
            "source": "stock_price",
            "status": "error",
            "error": str(e)
        })

    # --- Stock News Data Block (Last 7 Days) ---
    try:
        today = datetime.utcnow().date()
        seven_days_ago = today - timedelta(days=7)
        from_date = seven_days_ago.isoformat()
        to_date = today.isoformat()

        for ticker in tickers_list:
            news_url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={from_date}&to={to_date}&token={FINNHUB_API_KEY}"
            news_res = requests.get(news_url)
            news_data = news_res.json()

            gcs_filename = f"stock_news_{ticker}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            bucket = gcs_client.bucket(GCS_BUCKET)
            blob = bucket.blob(gcs_filename)

            blob.upload_from_string(
                data=json.dumps(news_data),
                content_type='application/json'
            )

            fs_client.collection('logs').add({
                "source": "stock_news",
                "status": "uploaded",
                "filename": gcs_filename,
                "timestamp": timestamp
            })

    except Exception as e:
        fs_client.collection('logs').add({
            "source": "stock_news",
            "status": "error",
            "error": str(e)
        })

    return ("✅ Stock Price + News Pipeline Completed", 200)
