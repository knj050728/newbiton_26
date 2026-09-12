from subway import get_subway_options
from taxi import get_taxi_info


# ==================================================
# 역 이름 정규화
#
# "잠실역" -> "잠실"
# "잠실"   -> "잠실"
# ==================================================
def normalize_station(name):

    if name is None:
        return ""

    name = str(name).strip()

    if name.endswith("역"):
        name = name[:-1]

    return name


# ==================================================
# 택시 검색용 역 이름
#
# "합정" -> "합정역"
# ==================================================
def station_for_taxi(name):

    name = str(name).strip()

    if not name.endswith("역"):
        name += "역"

    return name


# ==================================================
# 추천 함수
# ==================================================
def get_recommendations(
    start,
    destination,
    departure_time,
    budget
):

    start = start.strip()
    destination = destination.strip()

    hour = int(
        departure_time.split(":")[0]
    )

    print("\n")
    print("========================================")
    print("집갈각 추천 계산 시작")
    print("========================================")

    print("출발지:", start)
    print("도착지:", destination)
    print("출발시간:", departure_time)
    print("택시예산:", budget)


    # ==================================================
    # 1. 지하철 후보 조회
    # ==================================================
    try:

        subway_options = get_subway_options(
            start,
            destination,
            departure_time
        )

    except Exception as e:

        print(
            "지하철 후보 조회 오류:",
            type(e).__name__,
            e
        )

        subway_options = []


    if subway_options is None:
        subway_options = []


    print("\n===== subway_options =====")

    for option in subway_options:
        print(option)


    # ==================================================
    # 2. 목적지까지 지하철로 갈 수 있는지 확인
    # ==================================================
    destination_option = None


    for option in subway_options:

        if not option.get(
            "available",
            False
        ):
            continue


        station = option.get(
            "station",
            ""
        )


        if (
            normalize_station(station)
            == normalize_station(destination)
        ):

            destination_option = option
            break


    # ==================================================
    # 3. 목적지까지 지하철로 갈 수 있으면
    #
    # 택시를 계산하지 않는다.
    # ==================================================
    if destination_option is not None:

        print("\n========================================")
        print("목적지까지 대중교통 이용 가능")
        print("→ 택시 계산 생략")
        print("========================================")


        subway_time = int(
            destination_option.get(
                "subway_time",
                0
            )
        )


        subway_cost = int(
            destination_option.get(
                "subway_cost",
                0
            )
        )


        transit_plan = {

            "type":
                "TRANSIT",

            "station":
                destination_option["station"],

            "total_time":
                subway_time,

            "total_cost":
                subway_cost,

            "subway_time":
                subway_time,

            "taxi_time":
                0,

            "subway_cost":
                subway_cost,

            "taxi_cost":
                0,

            "within_budget":
                True
        }


        print(
            "대중교통 추천:",
            transit_plan
        )


        return {

            "save":
                transit_plan,

            "balance":
                transit_plan,

            "fast":
                transit_plan,

            "all_plans":
                [transit_plan]
        }


    # ==================================================
    # 여기까지 왔다는 뜻:
    #
    # 목적지까지 지하철로 못 감
    #
    # → 이제부터 HYBRID / TAXI 계산
    # ==================================================

    print("\n========================================")
    print("목적지까지 대중교통만으로 이동 불가")
    print("→ HYBRID / TAXI 계산 시작")
    print("========================================")


    plans = []


    # ==================================================
    # 4. 갈 수 있는 역까지 지하철 + 택시
    # ==================================================
    for option in subway_options:

        if not option.get(
            "available",
            False
        ):
            continue


        station = str(
            option.get(
                "station",
                ""
            )
        ).strip()


        if not station:
            continue


        subway_time = int(
            option.get(
                "subway_time",
                0
            )
        )


        subway_cost = int(
            option.get(
                "subway_cost",
                0
            )
        )


        print("\n----------------------------------------")
        print("HYBRID 후보역:", station)


        taxi_start = station_for_taxi(
            station
        )


        try:

            taxi = get_taxi_info(
                taxi_start,
                destination,
                hour
            )

        except Exception as e:

            print(
                "택시 계산 오류:",
                type(e).__name__,
                e
            )

            taxi = None


        print(
            "후보역 택시 결과:",
            taxi
        )


        if taxi is None:

            print(
                "→ 택시 계산 실패, 후보 제외"
            )

            continue


        try:

            taxi_time = int(
                taxi["time"]
            )

            taxi_fare = int(
                taxi["fare"]
            )

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            print(
                "→ 택시 데이터 오류"
            )

            continue


        if taxi_time <= 0:
            continue


        if taxi_fare <= 0:
            continue


        total_time = (
            subway_time
            + taxi_time
        )


        total_cost = (
            subway_cost
            + taxi_fare
        )


        hybrid_plan = {

            "type":
                "HYBRID",

            "station":
                station,

            "total_time":
                total_time,

            "total_cost":
                total_cost,

            "subway_time":
                subway_time,

            "taxi_time":
                taxi_time,

            "subway_cost":
                subway_cost,

            "taxi_cost":
                taxi_fare,

            "within_budget":
                taxi_fare <= budget
        }


        plans.append(
            hybrid_plan
        )


        print(
            "HYBRID 후보 추가:",
            hybrid_plan
        )


    # ==================================================
    # 5. 택시 직행
    # ==================================================
    print("\n========================================")
    print("직행 택시 계산")
    print("========================================")


    try:

        direct_taxi = get_taxi_info(
            start,
            destination,
            hour
        )

    except Exception as e:

        print(
            "직행 택시 오류:",
            type(e).__name__,
            e
        )

        direct_taxi = None


    print(
        "직행 택시 결과:",
        direct_taxi
    )


    if direct_taxi is not None:

        try:

            direct_time = int(
                direct_taxi["time"]
            )

            direct_fare = int(
                direct_taxi["fare"]
            )

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            direct_time = 0
            direct_fare = 0


        if (
            direct_time > 0
            and direct_fare > 0
        ):

            direct_plan = {

                "type":
                    "TAXI",

                "station":
                    None,

                "total_time":
                    direct_time,

                "total_cost":
                    direct_fare,

                "subway_time":
                    0,

                "taxi_time":
                    direct_time,

                "subway_cost":
                    0,

                "taxi_cost":
                    direct_fare,

                "within_budget":
                    direct_fare <= budget
            }


            plans.append(
                direct_plan
            )


            print(
                "TAXI 후보 추가:",
                direct_plan
            )


    # ==================================================
    # 6. 아무 후보도 없으면 종료
    # ==================================================
    if not plans:

        print(
            "추천 가능한 경로가 없습니다."
        )

        return None


    # ==================================================
    # 7. 후보 분리
    # ==================================================
    hybrid_plans = [
        plan
        for plan in plans
        if plan["type"] == "HYBRID"
    ]


    taxi_plans = [
        plan
        for plan in plans
        if plan["type"] == "TAXI"
    ]


    print("\n========================================")
    print("후보 현황")
    print("========================================")

    print(
        "HYBRID:",
        len(hybrid_plans)
    )

    print(
        "TAXI:",
        len(taxi_plans)
    )


    # ==================================================
    # 8. SAVE
    #
    # 가장 저렴
    # ==================================================
    save = min(
        plans,
        key=lambda x:
            x["total_cost"]
    )


    # ==================================================
    # 9. FAST
    #
    # 가장 빠름
    # ==================================================
    fast = min(
        plans,
        key=lambda x:
            x["total_time"]
    )


    # ==================================================
    # 10. BALANCE
    #
    # 예산 안 HYBRID 중 가장 빠른 경로
    # ==================================================
    affordable_hybrids = [

        plan

        for plan in hybrid_plans

        if plan["taxi_cost"] <= budget
    ]


    if affordable_hybrids:

        balance = min(
            affordable_hybrids,
            key=lambda x:
                x["total_time"]
        )


    elif hybrid_plans:

        # HYBRID가 전부 예산 초과
        # → 택시비 가장 저렴한 HYBRID
        balance = min(
            hybrid_plans,
            key=lambda x:
                x["taxi_cost"]
        )


    else:

        # HYBRID 자체가 없으면
        # 직행 택시 등 남은 후보 사용
        balance = save


    # ==================================================
    # 11. 최종 결과
    # ==================================================
    print("\n========================================")
    print("최종 추천")
    print("========================================")

    print(
        "SAVE:",
        save
    )

    print(
        "BALANCE:",
        balance
    )

    print(
        "FAST:",
        fast
    )


    return {

        "save":
            save,

        "balance":
            balance,

        "fast":
            fast,

        "all_plans":
            plans
    }


# ==================================================
# 단독 테스트
# ==================================================
if __name__ == "__main__":

    result = get_recommendations(
        "강남역",
        "홍대입구역",
        "23:30",
        11000
    )


    if result is None:

        print(
            "추천 가능한 경로가 없습니다."
        )

    else:

        print("\n====================")
        print("최종 추천 결과")
        print("====================")

        print(
            "SAVE:",
            result["save"]
        )

        print(
            "BALANCE:",
            result["balance"]
        )

        print(
            "FAST:",
            result["fast"]
        )