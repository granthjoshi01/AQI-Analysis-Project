# AQI-Analysis-Project

📈 AQI Data Engineering & Delhi Pollution Analysis Project

🔥 Project Overview

This project is a complete end-to-end data engineering + analytics pipeline that collects real-time AQI data, processes it, visualizes trends, and explains why Delhi consistently experiences high air pollution levels.

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
