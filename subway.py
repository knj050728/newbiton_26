import requests
from datetime import datetime


# =========================================================
# 서울시 Open API 인증키
# =========================================================
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")


# =========================================================
# 2호선 본선 전체
# 순서는 외선 방향 기준
#
# 외선 = INOUT_TAG 2
# 내선 = INOUT_TAG 1
# =========================================================
LINE2 = [
    {"station": "시청역", "code": "201"},
    {"station": "을지로입구역", "code": "202"},
    {"station": "을지로3가역", "code": "203"},
    {"station": "을지로4가역", "code": "204"},
    {"station": "동대문역사문화공원역", "code": "205"},
    {"station": "신당역", "code": "206"},
    {"station": "상왕십리역", "code": "207"},
    {"station": "왕십리역", "code": "208"},
    {"station": "한양대역", "code": "209"},
    {"station": "뚝섬역", "code": "210"},
    {"station": "성수역", "code": "211"},
    {"station": "건대입구역", "code": "212"},
    {"station": "구의역", "code": "213"},
    {"station": "강변역", "code": "214"},
    {"station": "잠실나루역", "code": "215"},
    {"station": "잠실역", "code": "216"},
    {"station": "잠실새내역", "code": "217"},
    {"station": "종합운동장역", "code": "218"},
    {"station": "삼성역", "code": "219"},
    {"station": "선릉역", "code": "220"},
    {"station": "역삼역", "code": "221"},
    {"station": "강남역", "code": "222"},
    {"station": "교대역", "code": "223"},
    {"station": "서초역", "code": "224"},
    {"station": "방배역", "code": "225"},
    {"station": "사당역", "code": "226"},
    {"station": "낙성대역", "code": "227"},
    {"station": "서울대입구역", "code": "228"},
    {"station": "봉천역", "code": "229"},
    {"station": "신림역", "code": "230"},
    {"station": "신대방역", "code": "231"},
    {"station": "구로디지털단지역", "code": "232"},
    {"station": "대림역", "code": "233"},
    {"station": "신도림역", "code": "234"},
    {"station": "문래역", "code": "235"},
    {"station": "영등포구청역", "code": "236"},
    {"station": "당산역", "code": "237"},
    {"station": "합정역", "code": "238"},
    {"station": "홍대입구역", "code": "239"},
    {"station": "신촌역", "code": "240"},
    {"station": "이대역", "code": "241"},
    {"station": "아현역", "code": "242"},
    {"station": "충정로역", "code": "243"},
]


# =========================================================
# 역명 정리
# "홍대입구" / "홍대입구역" 둘 다 처리
# =========================================================
def normalize_station_name(name):

    if name is None:
        return ""

    name = name.strip()

    if name.endswith("역"):
        name = name[:-1]

    return name


# =========================================================
# LINE2에서 역 찾기
# =========================================================
def find_station_index(name):

    target = normalize_station_name(name)

    for index, station in enumerate(LINE2):

        current = normalize_station_name(
            station["station"]
        )

        if current == target:
            return index

    return None


# =========================================================
# API 종착역명 -> LINE2 index 찾기
# =========================================================
def find_terminal_index(name):

    target = normalize_station_name(name)

    # 정확히 일치
    for index, station in enumerate(LINE2):

        current = normalize_station_name(
            station["station"]
        )

        if current == target:
            return index

    # API 문자열에 부가 문자가 붙어있는 경우 대비
    for index, station in enumerate(LINE2):

        current = normalize_station_name(
            station["station"]
        )

        if current in target:
            return index

    return None


# =========================================================
# 요일
#
# 평일 1
# 토요일 2
# 일요일/공휴일 3
# =========================================================
def get_week_tag():

    weekday = datetime.now().weekday()

    if weekday <= 4:
        return "1"

    elif weekday == 5:
        return "2"

    return "3"


# =========================================================
# 시간 -> 분
# =========================================================
def time_to_minutes(time_string):

    parts = time_string.split(":")

    hour = int(parts[0])
    minute = int(parts[1])

    # 새벽 시간은 다음날로 취급
    if hour < 4:
        hour += 24

    return hour * 60 + minute


def input_time_to_minutes(time_string):

    hour, minute = map(
        int,
        time_string.split(":")
    )

    if hour < 4:
        hour += 24

    return hour * 60 + minute


# =========================================================
# 해당 역 막차/심야 시간표 조회
#
# direction
# 1 = 내선
# 2 = 외선
# =========================================================
def get_last_train_rows(
    station_code,
    direction
):

    week_tag = get_week_tag()

    url = (
        f"http://openapi.seoul.go.kr:8088/"
        f"{SEOUL_API_KEY}/json/"
        f"SearchLastTrainTimeByFRCodeService/"
        f"1/1000/"
        f"{station_code}/"
        f"{week_tag}/"
        f"{direction}"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

    except Exception as e:

        print(
            "서울시 막차 API 오류:",
            e
        )

        return []

    result = data.get(
        "SearchLastTrainTimeByFRCodeService"
    )

    if result is None:

        print(
            "서울시 API 응답 오류:",
            data
        )

        return []

    return result.get(
        "row",
        []
    )


# =========================================================
# 출발시간 이후 가장 빠른 열차 찾기
# =========================================================
def find_next_train(
    station_code,
    departure_time,
    direction
):

    rows = get_last_train_rows(
        station_code,
        direction
    )

    requested = input_time_to_minutes(
        departure_time
    )

    candidates = []

    for row in rows:

        left_time = row.get("LEFTTIME")
        terminal = row.get("SUBWAYENAME")

        if not left_time:
            continue

        train_minutes = time_to_minutes(
            left_time
        )

        if train_minutes < requested:
            continue

        terminal_index = find_terminal_index(
            terminal
        )

        # 2호선 본선 종착역만 사용
        if terminal_index is None:
            continue

        candidates.append({
            "departure": left_time,
            "departure_minutes": train_minutes,
            "terminal": terminal,
            "terminal_index": terminal_index,
            "direction": direction
        })

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: x["departure_minutes"]
    )

    return candidates[0]


# =========================================================
# 출발역 → 종착역까지 실제 진행 역 생성
#
# direction 2 = 외선 = 리스트 + 방향
# direction 1 = 내선 = 리스트 - 방향
# =========================================================
def build_route(
    start_index,
    terminal_index,
    direction
):

    route = []

    current = start_index

    # 순환선 무한루프 방지
    for _ in range(len(LINE2) - 1):

        if direction == "2":
            current = (
                current + 1
            ) % len(LINE2)

        else:
            current = (
                current - 1
            ) % len(LINE2)

        route.append(current)

        if current == terminal_index:
            break

    return route


# =========================================================
# 예상 지하철 이동시간
#
# 오늘 MVP:
# 역당 평균 약 2.3분 사용
#
# 막차 탑승 가능 여부 자체는
# 실제 서울시 API 사용
# =========================================================
def calculate_subway_time(
    stop_count
):

    return round(
        stop_count * 2.3
    )


# =========================================================
# 한 방향 후보 생성
# =========================================================
def make_direction_options(
    start_index,
    destination_index,
    departure_time,
    direction
):

    start_station = LINE2[start_index]

    train = find_next_train(
        start_station["code"],
        departure_time,
        direction
    )

    if train is None:

        print(
            f"방향 {direction}: "
            "이용 가능한 열차 없음"
        )

        return []

    print()
    print(
        "방향:",
        "외선" if direction == "2" else "내선"
    )
    print(
        "탑승 열차:",
        train["departure"]
    )
    print(
        "종착역:",
        train["terminal"]
    )

    route_indices = build_route(
        start_index,
        train["terminal_index"],
        direction
    )

    options = []

    for stop_number, station_index in enumerate(
        route_indices,
        start=1
    ):

        station = LINE2[
            station_index
        ]

        subway_time = calculate_subway_time(
            stop_number
        )

        options.append({
            "station": station["station"],
            "subway_time": subway_time,
            "subway_cost": 1650,
            "available": True
        })

        # 목적지까지 지하철로 도달했으면
        # 그 이후 역은 굳이 후보로 만들지 않음
        if station_index == destination_index:
            break

    return options


# =========================================================
# recommend.py에서 사용하는 함수
# =========================================================
def get_subway_options(
    start,
    destination,
    departure_time
):

    start_index = find_station_index(
        start
    )

    destination_index = find_station_index(
        destination
    )

    if start_index is None:

        print(
            f"2호선 역을 찾을 수 없습니다: {start}"
        )

        return []

    if destination_index is None:

        print(
            f"현재 지하철 MVP는 "
            f"2호선 목적지만 지원합니다: {destination}"
        )

        return []

    if start_index == destination_index:
        return []

    print()
    print(
        "===== 2호선 전체 경로 탐색 ====="
    )
    print(
        "출발:",
        LINE2[start_index]["station"]
    )
    print(
        "도착:",
        LINE2[destination_index]["station"]
    )
    print(
        "시간:",
        departure_time
    )

    # 외선 후보
    outer_options = make_direction_options(
        start_index,
        destination_index,
        departure_time,
        "2"
    )

    # 내선 후보
    inner_options = make_direction_options(
        start_index,
        destination_index,
        departure_time,
        "1"
    )

    # 두 방향 후보 합치기
    all_options = (
        outer_options
        + inner_options
    )

    # 같은 역 중복 제거
    unique = {}

    for option in all_options:

        name = option["station"]

        if name not in unique:

            unique[name] = option

        else:

            # 더 빠른 지하철 경로 유지
            if (
                option["subway_time"]
                <
                unique[name]["subway_time"]
            ):
                unique[name] = option

    result = list(
        unique.values()
    )

    print()
    print(
        "===== 최종 지하철 후보 ====="
    )

    for option in result:
        print(option)

    return result


# =========================================================
# 단독 테스트
# =========================================================
if __name__ == "__main__":

    result = get_subway_options(
        "강남역",
        "홍대입구역",
        "23:30"
    )

    print()
    print(
        "===== 최종 결과 ====="
    )

    for option in result:
        print(option)