# Weather Data Pipeline using Google Cloud Platform

## Overview

This project automates the process of fetching real-time weather data from OpenWeatherMap API and stores it in Google BigQuery and Firestore using Google Cloud Functions and Cloud Scheduler.

## Architecture

```mermaid
graph TD
    A[Cloud Scheduler (1-minute cron)] --> B[Cloud Function: fetch_and_store_weather]
    B --> C[OpenWeatherMap API]
    B --> D[Firestore (logs)]
    B --> E[BigQuery (weather_stream table)]
```

## Features

* **Scheduled data collection** every minute using Cloud Scheduler
* **Data cleaning & validation** in Cloud Function
* **Storage in BigQuery** for analytics
* **Storage in Firestore** for logging and debugging
* **Auto-scaling and serverless setup**
* **Public API data ingestion**

## Tools and Services Used

* Google Cloud Platform (GCP)
* Cloud Functions (Gen 1)
* Cloud Scheduler
* BigQuery (Distributed storage/processing)
* Firestore (NoSQL database)
* OpenWeatherMap API (External data source)

## Setup Instructions

### 1. Enable Required APIs

```bash
gcloud services enable cloudfunctions.googleapis.com \
    firestore.googleapis.com \
    bigquery.googleapis.com \
    cloudscheduler.googleapis.com
```

### 2. Create BigQuery Dataset and Table

```sql
CREATE DATASET IF NOT EXISTS weather_data;
CREATE TABLE IF NOT EXISTS weather_data.weather_stream (
    city STRING,
    temperature FLOAT64,
    humidity INT64,
    pressure INT64,
    wind_speed FLOAT64,
    timestamp TIMESTAMP
);
```

### 3. Create Firestore Database

Use Firestore in Native mode.

### 4. Deploy the Cloud Function

```bash
gcloud functions deploy fetch_and_store_weather \
  --runtime python310 \
  --trigger-http \
  --entry-point fetch_and_store_weather \
  --region=us-central1 \
  --allow-unauthenticated
```

### 5. Create the Scheduler Job

```bash
gcloud scheduler jobs create http fetch-weather-job \
  --schedule="*0 * * * *" \
  --uri="https://us-central1-.cloudfunctions.net/fetch_and_store_weather" \
  --http-method=GET \
  --location=us-central1 \
  --time-zone="UTC"
```

## Cloud Function Code (`main.py`)

```python
import requests
import json
from google.cloud import bigquery, firestore
from datetime import datetime

API_KEY = 'd9b627d91ab4a26e7789d9e606d74593'
CITY = 'Karachi'

bq_client = bigquery.Client()
fs_client = firestore.Client()

def fetch_and_store_weather(request):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        res = requests.get(url)
        weather_data = res.json()

        data = {
            "city": CITY,
            "temperature": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "pressure": weather_data["main"]["pressure"],
            "wind_speed": weather_data["wind"]["speed"],
            "timestamp": datetime.utcnow().isoformat()
        }

        table_id = 'sp25-i535-kkhawaja-portfolio.weather_data.weather_stream'
        bq_client.insert_rows_json(table_id, [data])

        fs_client.collection('logs').add({
            "status": "inserted",
            "data": data
        })

        return ("Success", 200)

    except Exception as e:
        fs_client.collection('logs').add({
            "status": "error",
            "error": str(e)
        })
        return ("Error", 500)
```

## Repository Structure

```
weather-data-pipeline/
├── cloud-function/
│   └── main.py
├── README.md
```

## Future Improvements

* Use Secret Manager for API keys
* Add retry & dead letter topics
* Visualization dashboard in Data Studio or Looker

## Author


