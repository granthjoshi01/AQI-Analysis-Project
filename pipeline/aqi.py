import requests

url = "https://api.openweathermap.org/data/2.5/air_pollution?lat=0&lon=0&appid=172d73aff141b30936ee738b97488e23"

response = requests.get(url)
data = response.json()

print(data)