import functions_framework
import requests
from google.cloud import bigquery
from google.cloud import firestore
API_KEY = 'JT23ILEL2CXN309W'  # Replace with your Finnhub API key

@functions_framework.http
def ingest_data(request):
    # Initialize clients
    bq_client = bigquery.Client()
    fs_client = firestore.Client()

    # 1. Fetch stock price (structured)
    stock_url = f'https://finnhub.io/api/v1/quote?symbol=AAPL&token={API_KEY}'
    stock_data = requests.get(stock_url).json()

    # Insert into BigQuery
    table_id = "sp25-i535-kkhawaja-portfolio.stock_data"  
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

    # 2. Fetch news (unstructured)
    news_url = f'https://finnhub.io/api/v1/news?category=general&token={API_KEY}'
    news = requests.get(news_url).json()

    for article in news[:5]:  # limit to 5
        fs_client.collection("market_news").add(article)

    return "Ingested stock and news data."