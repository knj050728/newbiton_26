def get_subway_options(start, destination, departure_time):

    # 해커톤 MVP용 대중교통 데모 데이터
    demo_routes = {

        ("홍대입구역", "잠실역"): [
            {
                "station": "왕십리역",
                "subway_time": 25,
                "subway_cost": 1500,
                "available": True
            },
            {
                "station": "건대입구역",
                "subway_time": 32,
                "subway_cost": 1500,
                "available": True
            },
            {
                "station": "종합운동장역",
                "subway_time": 43,
                "subway_cost": 1600,
                "available": True
            }
        ],

        ("강남역", "잠실역"): [
            {
                "station": "선릉역",
                "subway_time": 7,
                "subway_cost": 1400,
                "available": True
            },
            {
                "station": "삼성역",
                "subway_time": 11,
                "subway_cost": 1400,
                "available": True
            },
            {
                "station": "종합운동장역",
                "subway_time": 15,
                "subway_cost": 1400,
                "available": True
            }
        ],

        ("서울역", "잠실역"): [
            {
                "station": "동대문역사문화공원역",
                "subway_time": 12,
                "subway_cost": 1400,
                "available": True
            },
            {
                "station": "왕십리역",
                "subway_time": 20,
                "subway_cost": 1500,
                "available": True
            },
            {
                "station": "건대입구역",
                "subway_time": 28,
                "subway_cost": 1500,
                "available": True
            }
        ]
    }

    return demo_routes.get((start, destination), [])


if __name__ == "__main__":
    result = get_subway_options(
        "홍대입구역",
        "잠실역",
        "23:30"
    )

    print(result)