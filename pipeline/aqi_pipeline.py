"""AQI data collection pipeline for OpenWeather + CSV storage."""

import requests
import pandas as pd
from datetime import datetime
import os
import logging
import time
import json
from typing import Optional, Dict, List
import sys
from google_sheets_writer import write_dataframe_to_sheet

import warnings
from urllib3.exceptions import NotOpenSSLWarning
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Load API key from environment variable
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GOOGLE_DRIVE_DIR = "/Users/granthjoshi/Library/CloudStorage/GoogleDrive-granthjoshi611@gmail.com/My Drive/AQI_Project"
LOCAL_OUTPUT_FILE = os.path.join(BASE_DIR, "aqi_cleaned_data.csv")
CLOUD_OUTPUT_FILE = os.path.join(GOOGLE_DRIVE_DIR, "aqi_cleaned_data.csv")
LOG_FILE = os.path.join(BASE_DIR, "collection.log")
STATUS_FILE = os.path.join(BASE_DIR, "status.json")


MAX_RETRIES = 3
RETRY_DELAY = 60  
REQUEST_TIMEOUT = 15  


# Setup logging
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(LOG_FILE)]
    )


class AQIDataPipeline:
    """AQI data collection pipeline"""
    
    def __init__(self, api_key: str, local_output: str, cloud_output: str ):
        self.api_key = api_key
        self.local_output = local_output
        self.cloud_output = cloud_output 
        self.base_url = "https://api.openweathermap.org/data/2.5/air_pollution"
        
        self.cities = {
            'Delhi': {'lat': 28.6139, 'lon': 77.2090},
            'Udaipur': {'lat': 24.5854, 'lon': 73.7125}
        }
        
        logging.info("Pipeline initialized")
    
    def validate_api_key(self) -> bool:
        """Validate API key before starting collection"""
        try:
            test_url = f"{self.base_url}?lat=28.6139&lon=77.2090&appid={self.api_key}"
            response = requests.get(test_url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 401:
                logging.error("Invalid API key!")
                return False
            elif response.status_code == 200:
                logging.info("API key validated successfully")
                return True
            else:
                logging.warning(f"API validation returned status {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"API validation failed: {e}")
            return False
    
    def fetch_raw_data(self, city_name: str, retry_count: int = 0) -> Optional[Dict]:

        """Fetch AQI data for a city with retry logic."""

        coords = self.cities[city_name]
        url = f"{self.base_url}?lat={coords['lat']}&lon={coords['lon']}&appid={self.api_key}"
        
        try:
            logging.info(f"Fetching data for {city_name} (attempt {retry_count + 1}/{MAX_RETRIES})")
            
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            # Validate response structure
            if 'list' not in data or len(data['list']) == 0:
                raise ValueError("Invalid API response structure")
            
            aqi_info = data['list'][0]
            
            if 'main' not in aqi_info or 'components' not in aqi_info:
                raise ValueError("Missing required fields in API response")
            
            components = aqi_info['components']
            
            result = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'city': city_name,
                'aqi': aqi_info['main']['aqi'],
                'pm2_5': components.get('pm2_5', 0),
                'pm10': components.get('pm10', 0),
                'no2': components.get('no2', 0),
                'so2': components.get('so2', 0),
                'co': components.get('co', 0),
                'o3': components.get('o3', 0),
                'nh3': components.get('nh3', 0)
            }
            
            logging.info(f"Successfully fetched {city_name}: AQI={result['aqi']}, PM2.5={result['pm2_5']}")
            return result
            
        except requests.exceptions.Timeout:
            logging.error(f"Timeout fetching {city_name}")
            
        except requests.exceptions.ConnectionError:
            logging.error(f"Connection error for {city_name}")
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logging.error(f"Authentication failed for {city_name}")
                return None  # Don't retry on auth errors
            elif e.response.status_code == 429:
                logging.error(f"Rate limit exceeded for {city_name}")
            else:
                logging.error(f"HTTP error {e.response.status_code} for {city_name}")
                
        except ValueError as e:
            logging.error(f"Data validation error for {city_name}: {e}")
            
        except Exception as e:
            logging.error(f"Unexpected error fetching {city_name}: {type(e).__name__} - {e}")
        
        # Retry logic
        if retry_count < MAX_RETRIES - 1:
            logging.info(f"Retrying {city_name} in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
            return self.fetch_raw_data(city_name, retry_count + 1)
        else:
            logging.error(f"Failed to fetch {city_name} after {MAX_RETRIES} attempts")
            return None
    
    def validate_data(self, data: Dict) -> bool:
        """Validate collected data"""
        required_fields = ['timestamp', 'city', 'aqi', 'pm2_5', 'pm10']
        
        for field in required_fields:
            if field not in data:
                logging.error(f"Missing required field: {field}")
                return False
        
        # Validate AQI range (1-5)
        if not 1 <= data['aqi'] <= 5:
            logging.warning(f"AQI out of range: {data['aqi']}")
            return False
        
        # Validate PM2.5 (should be non-negative and reasonable)
        if data['pm2_5'] < 0 or data['pm2_5'] > 2000:
            logging.warning(f"PM2.5 out of reasonable range: {data['pm2_5']}")
            return False
        
        return True
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the collected data"""
        try:
            logging.info("Starting data cleaning...")
            
            original_rows = len(df)
            
            # Remove duplicates
            df = df.drop_duplicates(subset=['timestamp', 'city'], keep='last')
            duplicates_removed = original_rows - len(df)
            if duplicates_removed > 0:
                logging.info(f"Removed {duplicates_removed} duplicate records")
            
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
            # Remove rows with invalid timestamps
            invalid_timestamps = df['timestamp'].isna().sum()
            if invalid_timestamps > 0:
                logging.warning(f"Removing {invalid_timestamps} rows with invalid timestamps")
                df = df.dropna(subset=['timestamp'])
            
            
            pollutant_columns = ['pm2_5', 'pm10', 'no2', 'so2', 'co', 'o3', 'nh3']
            for col in pollutant_columns:
                if col in df.columns:
                    missing_count = df[col].isna().sum()
                    if missing_count > 0:
                        logging.info(f"Filling {missing_count} missing values in {col}")
                        df[col].fillna(0, inplace=True)
            
            # Add analysis columns
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.day_name()
            df['month'] = df['timestamp'].dt.month_name()
            df['year'] = df['timestamp'].dt.year
            df['week_number'] = df['timestamp'].dt.isocalendar().week
            
            
            df['aqi_category'] = df['aqi'].map({
                1: 'Good',
                2: 'Fair', 
                3: 'Moderate',
                4: 'Poor',
                5: 'Very Poor'
            })
            
            # Remove extreme outliers (likely errors)
            outlier_mask = (df['pm2_5'] > 1500) | (df['pm10'] > 2000)
            outliers = outlier_mask.sum()
            if outliers > 0:
                logging.warning(f"Removing {outliers} extreme outlier records")
                df = df[~outlier_mask]
            
            # Sort by timestamp (newest first)
            df = df.sort_values('timestamp', ascending=False)
            
            logging.info(f"Data cleaning complete. Final row count: {len(df)}")
            return df
            
        except Exception as e:
            logging.error(f"Error during data cleaning: {e}")
            raise
    
    def save_data(self, new_data: List[Dict]) -> Optional[pd.DataFrame]:
        """Append new AQI records to the CSV and return all data."""
        try:
            # Convert new data to DataFrame
            new_df = pd.DataFrame(new_data)
            if len(new_df) == 0:
                logging.warning("No new data to save")
                return None
            # Load existing data if file exists
            if os.path.exists(self.local_output):
                try:
                    existing_df = pd.read_csv(self.local_output)
                    logging.info(f"Loaded {len(existing_df)} existing records")
                    # Combine datasets
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                except pd.errors.EmptyDataError:
                    logging.warning("Existing file is empty, starting fresh")
                    combined_df = new_df
                except Exception as e:
                    logging.error(f"Error reading existing file: {e}")
                    # Backup the corrupted file
                    backup_file = self.local_output.replace('.csv', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
                    os.rename(self.local_output, backup_file)
                    logging.info(f"Backed up corrupted file to {backup_file}")
                    combined_df = new_df
            else:
                logging.info("Creating new data file")
                combined_df = new_df
            # Clean the combined dataset
            cleaned_df = self.clean_data(combined_df)
            # Save to CSV with error handling
            try:
                # Create backup before overwriting
                if os.path.exists(self.local_output):
                    temp_backup = self.local_output + '.temp'
                    cleaned_df.to_csv(temp_backup, index=False)
                    os.replace(temp_backup, self.local_output)
                else:
                    cleaned_df.to_csv(self.local_output, index=False)
                logging.info(f"Data saved to {self.local_output}")
                logging.info(f"Total records: {len(cleaned_df)}")
                # Save cloud copy after successful local save
                try:
                    os.makedirs(os.path.dirname(self.cloud_output), exist_ok=True)
                except PermissionError:
                    logging.warning("Google Drive not available; skipping cloud save")
                    return cleaned_df
                cleaned_df.to_csv(self.cloud_output, index=False)
                logging.info(f"Cloud copy saved to {self.cloud_output}")
                return cleaned_df
            except PermissionError:
                logging.error(f"Permission denied writing to {self.local_output}. File may be open in another program.")
                return None
            except Exception as e:
                logging.error(f"Error saving file: {e}")
                return None
        except Exception as e:
            logging.error(f"Unexpected error in save_data: {e}")
            return None
    
    def save_status(self, status: str, records_collected: int, errors: List[str]):
        """Save collection status to JSON file"""
        try:
            status_data = {
                'last_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': status,
                'records_collected': records_collected,
                'errors': errors,
                'total_records_in_file': self.get_total_records()
            }
            
            with open(STATUS_FILE, 'w') as f:
                json.dump(status_data, f, indent=2)
                
            logging.info(f"Status saved: {status}")
            
        except Exception as e:
            logging.error(f"Error saving status: {e}")
    
    def get_total_records(self) -> int:
        """Get total number of records in CSV file"""
        try:
            if os.path.exists(self.local_output):
                df = pd.read_csv(self.local_output)
                return len(df)
            return 0
        except:
            return 0
    
    def collect_and_process(self) -> bool:
        """
        Main collection function with complete error handling
        
        Returns:
            True if successful, False if failed
        """
        start_time = datetime.now()
        errors = []
        
        try:
            logging.info("="*60)
            logging.info(f"Collection started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            logging.info("="*60)
            
            # Validate API key first
            if not self.validate_api_key():
                errors.append("API key validation failed")
                self.save_status("FAILED", 0, errors)
                return False
            
            # Collect data for all cities
            raw_data = []
            for city in self.cities.keys():
                city_data = self.fetch_raw_data(city)
                
                if city_data:
                    # Validate data
                    if self.validate_data(city_data):
                        raw_data.append(city_data)
                    else:
                        error_msg = f"Invalid data received for {city}"
                        logging.error(error_msg)
                        errors.append(error_msg)
                else:
                    error_msg = f"Failed to fetch data for {city}"
                    errors.append(error_msg)
            
            # Check if we got any data
            if not raw_data:
                logging.error("No data collected from any city!")
                self.save_status("FAILED", 0, errors)
                return False
            
            # Save data
            result_df = self.save_data(raw_data)

            if result_df is not None:
                # Write latest cleaned data to Google Sheets
                try:
                    write_dataframe_to_sheet(result_df)
                    logging.info("Google Sheet updated successfully")
                except Exception as e:
                    logging.error(f"Failed to update Google Sheet: {e}")

                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                logging.info("="*60)
                logging.info("Collection successful")
                logging.info(f"  Records collected: {len(raw_data)}")
                logging.info(f"  Total records in file: {len(result_df)}")
                logging.info(f"  Duration: {duration:.2f} seconds")
                logging.info("="*60)

                self.save_status("SUCCESS", len(raw_data), errors if errors else [])
                return True
            else:
                logging.error("Failed to save data")
                errors.append("Data save failed")
                self.save_status("FAILED", len(raw_data), errors)
                return False
                
        except Exception as e:
            error_msg = f"Unexpected error in main collection: {type(e).__name__} - {e}"
            logging.error(error_msg)
            errors.append(error_msg)
            self.save_status("FAILED", 0, errors)
            return False



def main():
    """Main execution with comprehensive error handling"""
    
    try:
        # Validate configuration
        if not API_KEY:
            logging.error("OPENWEATHER_API_KEY environment variable not set")
            return 1
        
        # Create output directory if it doesn't exist
        if not os.path.exists(BASE_DIR):
           os.makedirs(BASE_DIR, exist_ok=True)
           #logging.info(f"Created base directory: {BASE_DIR}")
        
        # Initialize and run pipeline
        pipeline = AQIDataPipeline(API_KEY,LOCAL_OUTPUT_FILE,CLOUD_OUTPUT_FILE)
        success = pipeline.collect_and_process()
        
        # Return exit code (0 = success, 1 = failure)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logging.info("Collection interrupted by user")
        return 1
        
    except Exception as e:
        logging.error(f"Fatal error: {type(e).__name__} - {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

