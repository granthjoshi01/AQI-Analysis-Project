## AQI Analysis & Live Monitoring Pipeline

An automated data pipeline that collects real-time air quality data from OpenWeather, maintains a historical dataset, syncs it to Google Sheets, and powers a live analytics dashboard.


## Tech Stack

 **Programming Language**
- **Python 3.9+**

 **Data Collection**
- **OpenWeather Air Pollution API** – real-time AQI and pollutant data

 **Data Processing & Storage**
- **pandas** – data cleaning, transformation, and enrichment
- **CSV** – append-only historical storage (source of truth)

**Automation & Scheduling**
- **macOS launchd** – scheduled execution of the data pipeline

**Cloud & Integration**
- **Google Cloud Platform**
  - Google Sheets API
  - Google Drive API
  - Service Account authentication

**Analytics & Visualization**
- **Google Sheets** – live, shareable data mirror
- **Looker Studio** – real-time dashboard and visual analytics

**Supporting Libraries**
- **requests** – HTTP requests to external APIs
- **gspread** – Google Sheets interaction
- **google-auth** – secure service account authentication
  
⸻

## Overview

This project implements an end-to-end AQI data workflow:

•	Periodically fetches air quality data for selected cities

•	Cleans, validates, and stores data locally as a CSV

•	Maintains full historical records (append-only)

•	Mirrors the dataset to Google Sheets for live analytics

•	Supports real-time dashboards (e.g. Looker Studio)

•	Designed to run unattended via macOS launchd

The system is built with data integrity, automation, and clarity as primary goals.

## Files Explained

**1. aqi_pipeline.py**

Purpose:
Main production pipeline that orchestrates the entire AQI data workflow.

Responsibilities:

	•	Fetch AQI data from OpenWeather for configured cities
	•	Validate API responses and pollutant values
	•	Append new observations to a historical CSV
	•	Enrich data with time-based analytics fields
	•	Remove duplicates and invalid records
	•	Backup the dataset to Google Drive
	•	Trigger Google Sheets synchronization
	•	Log execution details and pipeline status

Key Design Choices:

•	Environment-based API key 
	
•	Append-only historical storage

•	Atomic file writes to prevent corruption

•	Defensive error handling and retries
	

⸻

**2. google_sheets_writer.py**

Purpose:
Dedicated writer module that mirrors the local CSV dataset to Google Sheets.

Responsibilities:

	•	Authenticate using a Google service account
	•	Normalize data types for strict Google Sheets API requirements
	•	Convert timestamps and date objects to safe string formats
	•	Clear and fully rewrite the worksheet on each run
	•	Ensure Google Sheets exactly matches the local CSV

Design Philosophy:

•	Google Sheets is treated as a read-only mirror

•	The local CSV is the single source of truth

•	No partial or incremental writes (prevents data drift)

⸻

**3. test_openweather_api.py (API test script)**

Purpose:
One-time diagnostic script to validate the OpenWeather API key and endpoint.

What it verifies:

  •	API key validity

  •	Network connectivity

  •	Response schema correctness

  •	Pollutant values for known coordinates


⸻

**4. test_google_sheets.py (Sheets test script)**

Purpose:
One-time diagnostic script to validate Google Sheets API access.

What it verifies:

•	Service account authentication

•	Spreadsheet access permissions

•	Ability to write data to a worksheet

## Python Dependencies

Install dependencies using:

        pip install requests pandas gspread google-auth google-auth-oauthlib google-auth-httplib2 urllib3
        
## Environment Setup

    export OPENWEATHER_API_KEY="your_api_key_here"

## To run manually:

    python aqi_pipeline.py
