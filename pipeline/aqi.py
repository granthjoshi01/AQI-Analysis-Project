#enter your API KEY in url
import requests

url = "https://api.openweathermap.org/data/2.5/air_pollution?lat=0&lon=0&appid=API_KEY"

response = requests.get(url)
data = response.json()

print(data)
