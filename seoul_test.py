import requests

SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")

station = "홍대입구"

url = (
    f"http://swopenapi.seoul.go.kr/api/subway/"
    f"{SEOUL_API_KEY}/json/realtimeStationArrival/0/5/{station}"
)

response = requests.get(url, timeout=10)

print("상태코드:", response.status_code)
print(response.text)