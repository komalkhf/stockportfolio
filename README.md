# Weather Data Pipeline using Google Cloud Platform

## Overview

This project automates the ingestion of real-time stock prices data and news data from Finnhub API and stores it in Google BigQuery, Firestore and Google cloud storage using Google Cloud Functions and Cloud Scheduler.

Data is fetched at 5-minutes intervals during pre-market, market hours and after-hours trading on weekdays using Cloud Scheduler to trigger Cloud Function.

We have ingested portfolio as a csv in bucket and used it in bigquery for analysis and visualization in looker studio.


## Architecture

    A[Cloud Scheduler (1-minute cron)] --> B[Cloud Function: fetch_and_store_weather]
    B --> C[OpenWeatherMap API]
    B --> D[Firestore (logs)]
    B --> E[BigQuery (weather_stream table)]


## Features

* **Scheduled data collection** every minute using Cloud Scheduler
* **Data cleaning & validation** in Cloud Function
* **Storage in BigQuery** for analytics
* **Storage in Firestore** for logging and debugging
* **Auto-scaling and serverless setup**
* **Public API data ingestion**Finnhub API



## Setup Instructions

### 1. Enable Required APIs

```bash
gcloud services enable cloudfunctions.googleapis.com \
    firestore.googleapis.com \
    bigquery.googleapis.com \
    cloudscheduler.googleapis.com
```

### 2. Create BigQuery Dataset and Table


### 3. Create Firestore Database


### 4. Deploy the Cloud Function

```bash
gcloud functions deploy fetch_and_store_stock_data \
  --runtime python310 \
  --trigger-http \
  --entry-point fetch_and_store_weather \
  --region=us-central1 \
  --allow-unauthenticated
```

### 5. Create the Scheduler Job

```bash
gcloud scheduler jobs create http fetch-stock_data-job \
  --schedule="*0 * * * *" \
  --uri="https://us-central1-.cloudfunctions.net/fetch_and_store_weather" \
  --http-method=GET \
  --location=us-central1 \
  --time-zone="UTC"
```

## Cloud Function Code (`main.py`)

import requests
import json
from google.cloud import bigquery, firestore, storage
from datetime import datetime, timedelta

# FINNHUB Config 
FINNHUB_API_KEY = 'd0avurhr01qlq65q0280d0avurhr01qlq65q028g'
TICKERS = "SCHD,SCHG,NVDA,MSFT,LLY"
GCS_BUCKET = 'fpkkhawaja'

# GCP Clients
bq_client = bigquery.Client()
fs_client = firestore.Client()
gcs_client = storage.Client()

def fetch_and_store_stock_data(request):
    timestamp = datetime.utcnow().replace(microsecond=0).isoformat()
    tickers_list = TICKERS.split(',')

    #  Stock Price Data Block
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
                "timestamp": timestamp
            }

            errors = bq_client.insert_rows_json(
                'sp25-i535-kkhawaja-portfolio.stock_data.stock_price',
                [stock_payload]
            )
            if errors:
                print(f"[ERROR] BQ insert failed for {ticker}: {errors}")
            else:
                print(f"[INFO] Inserted stock_price for {ticker}")

            fs_client.collection('logs').add({
                "source": "stock_price",
                "status": "inserted",
                "data": stock_payload
            })

    except Exception as e:
        print(f"[EXCEPTION] stock_price block failed: {e}")
        fs_client.collection('logs').add({
            "source": "stock_price",
            "status": "error",
            "error": str(e)
        })

    # Stock News Data 
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
        print(f"[EXCEPTION] stock_news block failed: {e}")
        fs_client.collection('logs').add({
            "source": "stock_news",
            "status": "error",
            "error": str(e)
        })

    return ("✅ Stock Price + News Pipeline Completed", 200)



## Repository Structure

```
weather-data-pipeline/
├── cloud-function/
│   └── main.py
├── README.md
```

## Future Improvements

* Use Secret Manager for API keys




