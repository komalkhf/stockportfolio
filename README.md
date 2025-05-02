# Stock & News Ingestor using Google Cloud Functions

This project fetches stock data (structured) and market news (unstructured) from the Finnhub API, then stores:
- Stock data in **BigQuery**
- News articles in **Firestore**

---

## ✅ Step 1: GCP Project Setup

1. Open [Google Cloud Console](https://console.cloud.google.com) and select your **university GCP project**.
2. Enable the following APIs:
   - Cloud Functions API
   - Firestore API
   - BigQuery API
   - Cloud Logging API *(optional)*

3. Go to **IAM & Admin > IAM** and ensure your account has the following roles:
   - Cloud Functions Developer
   - Firestore User
   - BigQuery Data Editor

---

## ✅ Step 2: Firestore Setup

1. Go to: [https://console.cloud.google.com/firestore](https://console.cloud.google.com/firestore)
2. Click **Create Database**
3. Select **Start in test mode** (if available)
4. Choose **us-central1** or your preferred region

---

## ✅ Step 3: BigQuery Setup

1. Go to: [https://console.cloud.google.com/bigquery](https://console.cloud.google.com/bigquery)
2. Create a new dataset:
   - Name: `stock_data`
3. (Optional) Manually create a table named `prices`, or let Cloud Function insert the first row to auto-create

---

## ✅ Step 4: Project Folder Structure

```
stock_ingest/
├── main.py
└── requirements.txt
```

---

## ✅ Step 5: Cloud Function Code

**main.py**
```python
import functions_framework
import requests
from google.cloud import bigquery
from google.cloud import firestore

API_KEY = 'YOUR_API_KEY'  # Replace with your Finnhub API key

@functions_framework.http
def ingest_data(request):
    bq_client = bigquery.Client()
    fs_client = firestore.Client()

    stock_url = f'https://finnhub.io/api/v1/quote?symbol=AAPL&token={API_KEY}'
    stock_data = requests.get(stock_url).json()

    table_id = "YOUR_PROJECT_ID.stock_data.prices"  # Replace
    row = [{
        "symbol": "AAPL",
        "price": stock_data.get("c"),
        "high": stock_data.get("h"),
        "low": stock_data.get("l"),
        "time": stock_data.get("t"),
        "previous_close": stock_data.get("pc"),
        "todays_open": stock_data.get("o"),
        "volume": stock_data.get("v")
    }]
    errors = bq_client.insert_rows_json(table_id, row)
    if errors:
        print("BigQuery errors:", errors)

    news_url = f'https://finnhub.io/api/v1/news?category=general&token={API_KEY}'
    news = requests.get(news_url).json()

    for article in news[:5]:
        fs_client.collection("market_news").add(article)

    return "Ingested stock and news data."
```

**requirements.txt**
```
requests
google-cloud-bigquery
google-cloud-firestore
functions-framework
```

---

## ✅ Step 6: Local Testing (Optional)

```bash
pip install -r requirements.txt
functions-framework --target=ingest_data
```

Open: `http://localhost:8080`

---

## ✅ Step 7: Deploy to Cloud Functions

```bash
gcloud functions deploy ingest_data   --runtime python311   --trigger-http   --allow-unauthenticated   --entry-point ingest_data   --region us-central1
```

Once deployed, open the trigger URL to run the function.

---

## ✅ Replace These Placeholders
- `YOUR_API_KEY`: Your [Finnhub API Key](https://finnhub.io/)
- `YOUR_PROJECT_ID`: Your actual GCP project ID

---

## ✅ Optional Step 8: Monitor Logs

```bash
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=ingest_data" --limit 20
```

---

Let me know if you need a scheduler (cron job) to run this periodically.