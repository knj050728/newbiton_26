import requests

SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")

# 홍대입구역 외부코드
FR_CODE = "239"

# 평일 = 1
WEEK_TAG = "1"

# 하행/외선 = 2
INOUT_TAG = "2"

url = (
    f"http://openapi.seoul.go.kr:8088/"
    f"{SEOUL_API_KEY}/json/"
    f"SearchLastTrainTimeByFRCodeService/"
    f"1/1000/"
    f"{FR_CODE}/"
    f"{WEEK_TAG}/"
    f"{INOUT_TAG}"
)

response = requests.get(url, timeout=10)

print("상태코드:", response.status_code)

data = response.json()

print("\n===== 막차 API 결과 =====")

result = data.get("SearchLastTrainTimeByFRCodeService")

if result is None:
    print(data)

else:
    print("총 건수:", result.get("list_total_count"))

    rows = result.get("row", [])

    for row in rows[:20]:
        print(
            row.get("STATION_NM"),
            "→",
            row.get("SUBWAYENAME"),
            "| 출발:",
            row.get("LEFTTIME")
        )