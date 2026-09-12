import requests

# =========================================================
# Kakao REST API Key
# 네 기존 키를 여기에 넣기
# =========================================================
REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")


# =========================================================
# 1. 장소 이름 -> 좌표 변환
# =========================================================
def get_coordinates(place_name):

    url = "https://dapi.kakao.com/v2/local/search/keyword.json"

    headers = {
        "Authorization": f"KakaoAK {REST_API_KEY}"
    }

    params = {
        "query": place_name
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )

        data = response.json()

    except Exception as e:
        print("장소 검색 요청 오류:", e)
        return None

    if response.status_code != 200:
        print("장소 검색 API 오류:", data)
        return None

    documents = data.get("documents", [])

    if not documents:
        print(f"장소를 찾을 수 없습니다: {place_name}")
        return None

    place = documents[0]

    return {
        "x": place["x"],
        "y": place["y"]
    }


# =========================================================
# 2. 자동차 거리 / 시간 가져오기
# =========================================================
def get_car_route(start, end):

    start_coord = get_coordinates(start)
    end_coord = get_coordinates(end)

    if start_coord is None or end_coord is None:
        return None

    url = "https://apis-navi.kakaomobility.com/v1/directions"

    headers = {
        "Authorization": f"KakaoAK {REST_API_KEY}"
    }

    params = {
        "origin": f"{start_coord['x']},{start_coord['y']}",
        "destination": f"{end_coord['x']},{end_coord['y']}"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )

        data = response.json()

    except Exception as e:
        print("길찾기 요청 오류:", e)
        return None

    if response.status_code != 200:
        print("길찾기 API 오류:", data)
        return None

    # -----------------------------------------------------
    # Kakao 응답에 routes가 없는 경우
    # 프로그램 전체가 죽지 않고 해당 후보만 제외
    # -----------------------------------------------------
    routes = data.get("routes")

    if not routes:
        print(f"자동차 경로를 찾을 수 없습니다: {start} -> {end}")
        print("Kakao 응답:", data)
        return None

    first_route = routes[0]

    summary = first_route.get("summary")

    if summary is None:
        print(f"경로 summary가 없습니다: {start} -> {end}")
        print("Kakao 응답:", data)
        return None

    distance = summary.get("distance")
    duration = summary.get("duration")

    if distance is None or duration is None:
        print(f"거리/시간 정보가 없습니다: {start} -> {end}")
        return None

    # meter -> km
    distance_km = distance / 1000

    # second -> minute
    time_min = round(duration / 60)

    return {
        "distance": round(distance_km, 1),
        "time": time_min
    }


# =========================================================
# 3. 택시 예상 요금 계산
# =========================================================
def calculate_taxi_fare(distance_km, hour=23):

    # 해커톤 MVP용 단순 예상 요금
    # 기본요금 4,800원 + km당 1,000원 가정
    fare = 4800 + (distance_km * 1000)

    # 22:00 ~ 03:59 단순 야간 할증
    if hour >= 22 or hour < 4:
        fare *= 1.2

    return round(fare / 100) * 100


# =========================================================
# 4. recommend.py에서 사용하는 최종 함수
# =========================================================
def get_taxi_info(start, end, hour=23):

    route = get_car_route(start, end)

    if route is None:
        return None

    fare = calculate_taxi_fare(
        route["distance"],
        hour
    )

    return {
        "distance": route["distance"],
        "time": route["time"],
        "fare": fare
    }


# =========================================================
# 5. 단독 테스트
# =========================================================
if __name__ == "__main__":

    result = get_taxi_info(
        "홍대입구역",
        "잠실역",
        23
    )

    print()
    print("===== 택시 테스트 결과 =====")
    print(result)