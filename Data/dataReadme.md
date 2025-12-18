AQI Analysis Project — Data Dictionary & Access Guide

Data Overview
	•	Primary analytical data is stored as CSV files in the local Data/ directory of this repository.
	•	Redundant backup copies of all critical CSV files are stored on Google Drive.
	•	A live Google Spreadsheet mirrors the core dataset for quick inspection, lightweight edits, and sharing with collaborators.

The local CSV files are the canonical source of truth for all analyses and dashboards.

⸻

Local CSV Files

All local CSV files are version-controlled and should be treated as the project’s primary data source.

Usage
	•	Read locally in analysis scripts and notebooks, for example:

import pandas as pd
df = pd.read_csv("Data/processed_aqi_daily.csv")




⸻

Google Drive CSV Backups

To ensure data durability, periodic backups of key CSV files are maintained in a dedicated Google Drive folder.


This lightweight versioning supports easy rollback and historical comparison.

⸻

Live Google Spreadsheet

A live Google Sheets document provides a convenient, shareable view of key AQI tables and summary statistics,

note : its fetched inside a live dashboard

Spreadsheet link : https://docs.google.com/spreadsheets/d/1lbDIBplg5ONuxJjtqAfFaY5IqHj0SAYDNaj0z58xGuc/edit?gid=1097246749#gid=1097246749

Maintained as part of the AQI Analysis Project.
