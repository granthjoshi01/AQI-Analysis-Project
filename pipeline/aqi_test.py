import requests
import json

API_KEY = "172d73aff141b30936ee738b97488e23"  



def test_api_key():
    """Test if your API key works"""
    
    print("="*60)
    print("TESTING API KEY")
    print("="*60)
    
    # Test with Delhi coordinates
    lat, lon = 28.6139, 77.2090
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    
    print(f"\n Making API call...")
    print(f"URL: {url[:80]}...")
    
    try:
        response = requests.get(url, timeout=10)
        
        # Check status code
        print(f"\n Response Status: {response.status_code}")
        
        if response.status_code == 200:
            # Success!
            data = response.json()
            
            print("\nSUCCESS! Your API key works!")
            print("\n" + "="*60)
            print(" SAMPLE DATA FROM DELHI")
            print("="*60)
            
            aqi_data = data['list'][0]
            aqi = aqi_data['main']['aqi']
            components = aqi_data['components']
            
            print(f"\n🏙️  City: Delhi")
            print(f"📍 Coordinates: {lat}, {lon}")
            print(f"\n💨 Air Quality Index: {aqi}")
            print(f"   Category: {get_aqi_category(aqi)}")
            print(f"\n🔬 Pollutant Levels:")
            print(f"   PM2.5: {components.get('pm2_5', 'N/A')} μg/m³")
            print(f"   PM10:  {components.get('pm10', 'N/A')} μg/m³")
            print(f"   NO2:   {components.get('no2', 'N/A')} μg/m³")
            print(f"   SO2:   {components.get('so2', 'N/A')} μg/m³")
            print(f"   CO:    {components.get('co', 'N/A')} μg/m³")
            print(f"   O3:    {components.get('o3', 'N/A')} μg/m³")
            
            print("\n" + "="*60)
            print("🎉 ALL GOOD! You can proceed to next step")
            print("="*60)
            
            return True
            
        elif response.status_code == 401:
            print("\n❌ ERROR: Invalid API Key")
            print("\n🔧 Possible fixes:")
            print("   1. Check if you copied the key correctly")
            print("   2. Wait 10 minutes - new keys need activation time")
            print("   3. Go to https://home.openweathermap.org/api_keys")
            print("      and verify your key is active")
            return False
            
        elif response.status_code == 429:
            print("\n❌ ERROR: Too many requests")
            print("   You've hit the API limit. Wait an hour and try again.")
            return False
            
        else:
            print(f"\n❌ ERROR: Unexpected response code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Request timed out")
        print("   Check your internet connection and try again")
        return False
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("   Check your internet connection")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


def get_aqi_category(aqi_value):
    """Convert AQI number to category"""
    categories = {
        1: "Good 😊",
        2: "Fair 🙂",
        3: "Moderate 😐",
        4: "Poor 😟",
        5: "Very Poor 😷"
    }
    return categories.get(aqi_value, "Unknown")


def test_both_cities():
    """Test API for both Delhi and Udaipur"""
    
    cities = {
        'Delhi': {'lat': 28.6139, 'lon': 77.2090},
        'Udaipur': {'lat': 24.5854, 'lon': 73.7125}
    }
    
    print("\n" + "="*60)
    print("🌍 TESTING BOTH CITIES")
    print("="*60)
    
    for city_name, coords in cities.items():
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={coords['lat']}&lon={coords['lon']}&appid={API_KEY}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                aqi = data['list'][0]['main']['aqi']
                pm25 = data['list'][0]['components'].get('pm2_5', 0)
                
                print(f"\n✅ {city_name}")
                print(f"   AQI: {aqi} ({get_aqi_category(aqi)})")
                print(f"   PM2.5: {pm25} μg/m³")
            else:
                print(f"\n❌ {city_name}: Failed (Status {response.status_code})")
                
        except Exception as e:
            print(f"\n❌ {city_name}: Error - {str(e)}")
    
    print("\n" + "="*60)



if __name__ == "__main__":
    
    # Check if API key is set
    if API_KEY == "PASTE_YOUR_API_KEY_HERE":
        print("\n" + "="*60)
        print("  WARNING: API KEY NOT SET")
        print("="*60)
        print("\nPlease:")
        print("1. Open this script in a text editor")
        print("2. Find line 12: API_KEY = 'PASTE_YOUR_API_KEY_HERE'")
        print("3. Replace PASTE_YOUR_API_KEY_HERE with your actual API key")
        print("4. Save and run again")
        print("\n" + "="*60)
    else:
        # Run basic test
        success = test_api_key()
        
        # If basic test passes, test both cities
        if success:
            test_both_cities()
            
            print("\n" + "="*60)
            print("🚀 NEXT STEPS:")
            print("="*60)
            print("1. ✅ API key is working")
            print("2. ➡️  Now run the full data collection script")
            print("3. ➡️  Let it collect data for a few hours")
            print("4. ➡️  Connect Power BI to the CSV file")
            print("="*60)