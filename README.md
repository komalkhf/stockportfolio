# Real-time Stock Data Pipeline using Google Cloud Platform

## Overview

This project automates the ingestion of **real-time stock prices**, **portfolio data** (structured), and **news data** (unstructured) from the [Finnhub API](https://finnhub.io), storing them into **Google BigQuery**, **Firestore**, and **Cloud Storage** using serverless GCP services. Visualization is done via **Looker Studio** dashboards.


## Project Overview

## Key Features

- Real-time stock & news data ingestion using **Cloud Functions** + **Cloud Scheduler**
- **CSV portfolio data** upload and analysis in BigQuery
- **Unstructured news data** storage in Cloud Storage (JSON)
- **NoSQL logs** stored in Firestore
- Dynamic dashboards built in **Looker Studio**
- Completely serverless and scalable setup on Google Cloud


## Setup Instructions

### 1. Enable Required APIs
Enable the following in **API Library**:
- Cloud Storage
- Firestore
- BigQuery
- Cloud Functions
- Cloud Scheduler

### 2.IAM Roles
Ensure your IAM roles are set up for:
- Developer Account
- Service Account (Invoker for Cloud Functions)

## Pipeline Implementation Steps

### 1. Cloud Storage (News & Portfolio CSV)
Create bucket:
Bucket Name: kpkkhawaja
Region: us-central1
Upload portfolio data as CSV and fetch news data via Cloud Function to JSON.

### 2. Create BigQuery Dataset and Table
Fetch real time stock price data from API using cloud function and load to BigQuery.
Create:
Dataset: stock_data
Table: stock_price with appropriate schema.

Upload portfolio CSV from bucket.
Create:
Dataset: stock_data
Table:portfolio with appropriate schema

### 3. Create Firestore Database
Create Firestore in Native mode (Region: us-central1). Logs from Cloud Function will be stored here automatically.

### 4. Create the Scheduler Job
Schedule job to run every 5 minutes on weekdays during market trading time:
```bash
gcloud scheduler jobs create http fetch-stock_data-job \
  --schedule="*/5 * * * 1-5" \
  --uri="https://us-central1-.cloudfunctions.net/fetch_and_store_stock_data" \
  --http-method=GET \
  --location=us-central1 \
  --time-zone="UTC"
```

### 5. Cloud Function Code (`main.py`)

### 6. Deploy the Cloud Function

```bash
gcloud functions deploy fetch_and_store_stock_data \
  --runtime python310 \
  --trigger-http \
  --entry-point fetch_and_store_stock_data \
  --region=us-central1 \
  --allow-unauthenticated
```

### 7.Data analysis in BigQuery
Perform data analysis using SQL

### 8.Data Visualization in Looker
Perform data visualization in Looker

### Results
Real-time, automated ingestion of stock data
Scalable and efficient ETL pipeline
Unified analysis of structured and unstructured financial data
Insights on top/bottom performers, sector allocation, and portfolio value
Custom dashboard for stakeholders in Looker Studio



## Future Improvements

* Use Secret Manager for API keys
* Automate SQL queries execution and Looker Studio updates
* Integrate sentiment analysis on news data



