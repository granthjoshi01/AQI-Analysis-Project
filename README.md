 AQI Data Engineering & Delhi Pollution Analysis Project

 Problem Statement

Air quality disparities across Indian cities present a critical public health challenge.During a recent journey from Udaipur to Delhi, a stark contrast in air quality became immediately apparent— Delhi's persistent haze and respiratory discomfort and Udaipur's noticeably clearer skies and fresher air. This personal observation raised fundamental questions: What quantifiable differences exist between these cities? What systemic factors drive Delhi's chronic pollution crisis? And how can data-driven insights make these invisible threats visible?

 Project Overview

This project is a complete end-to-end data engineering + analytics pipeline that collects real-time AQI data, processes it, visualizes trends, and explains why Delhi consistently experiences high air pollution levels.

## 🔗 Live Resources

- **Live Dashboard**: https://lookerstudio.google.com/reporting/febbd29c-ea0e-42f7-8d8c-a951bbfe91c0
- **Live Google Sheet**:https://docs.google.com/spreadsheets/d/1lbDIBplg5ONuxJjtqAfFaY5IqHj0SAYDNaj0z58xGuc/edit?usp=sharing 





The project includes:
	•	✔ Real-time AQI Data Pipeline (ETL)
	•	✔ Interactive AQI Dashboard (Flask / Streamlit)
	•	✔ Analytical Report on Delhi AQI Trends
	•	✔ Visualizations (PM2.5, PM10, Seasonal Patterns)
	•	✔ Research-backed explanation of Delhi’s pollution causes

  # Project Structure

## Components

| Component    | Description                                    |
|-------------|------------------------------------------------|
| `pipeline/`  | Real-time AQI collection, cleaning, and storage |
| `dashboard/` | Web UI for AQI visualizations                   |
| `analysis/`  | Jupyter notebook + charts + explanation         |
| `data/`      | Cleaned datasets                                |
| `reports/`   | Final documented findings                       |

## Architecture (Simple Overview)
```
OpenWeather API → ETL Pipeline → Clean CSV → Dashboard → Insights / Report
```

## Workflow

1. **Data Collection**: The pipeline fetches real-time air quality data from the OpenWeather API
2. **ETL Process**: Data is extracted, transformed, and loaded into clean CSV format
3. **Visualization**: The dashboard provides interactive visualizations of AQI data
4. **Analysis**: Jupyter notebooks contain detailed analysis with charts and explanations
5. **Reporting**: Final insights and findings are documented in the reports directory
