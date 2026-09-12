from html import escape
from datetime import datetime, timedelta
from numbers import Real
from math import isfinite

import streamlit as st

from recommend import get_recommendations


st.set_page_config(
    page_title="집갈각",
    page_icon="🏠",
    layout="centered",
)


st.markdown(
    """
    <style>
    .stApp {
        background: #f7f8fa;
    }

    .block-container {
        max-width: 720px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }

    .hero {
        text-align: center;
        margin-bottom: 2rem;
    }

    .hero-title {
        color: #17191c;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.06em;
        margin-bottom: 0.35rem;
    }

    .hero-description {
        color: #68707c;
        font-size: 1.02rem;
        line-height: 1.6;
        margin: 0;
    }

    div[data-testid="stForm"] {
        background: white;
        border: 1px solid #e9ebef;
        border-radius: 22px;
        padding: 1.5rem 1.5rem 0.5rem;
        box-shadow: 0 10px 30px rgba(26, 31, 39, 0.06);
    }

    .stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        min-height: 3.2rem;
        border: 0;
        border-radius: 14px;
        background: #22262c;
        color: white;
        font-size: 1rem;
        font-weight: 700;
    }

    .stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        background: #0e1013;
        color: white;
        border: 0;
    }

    .result-heading {
        margin: 2.5rem 0 1rem;
    }

    .result-heading h2 {
        color: #20242a;
        font-size: 1.45rem;
        letter-spacing: -0.04em;
        margin-bottom: 0.25rem;
    }

    .result-heading p {
        color: #7b828d;
        margin: 0;
    }

    .route-card {
        background: white;
        border: 1px solid #e5e8ed;
        border-radius: 20px;
        padding: 1.45rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(26, 31, 39, 0.05);
    }

    .route-card.save { border-top: 5px solid #20a46b; }
    .route-card.balance { border-top: 5px solid #3478f6; }
    .route-card.fast { border-top: 5px solid #f2a42b; }

    .card-top {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.2rem;
    }

    .card-name {
        color: #25292f;
        font-size: 1.05rem;
        font-weight: 800;
        letter-spacing: 0.02em;
    }

    .card-time {
        color: #15181c;
        font-size: 1.35rem;
        font-weight: 800;
        text-align: right;
        white-space: nowrap;
    }

    .card-arrival {
        color: #7b828d;
        font-size: 0.88rem;
        font-weight: 600;
        text-align: right;
    }

    .card-price {
        color: #25292f;
        font-size: 1.25rem;
        font-weight: 800;
    }

    .timeline {
        margin: 0.2rem 0 1.1rem;
    }

    .timeline-stop {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        color: #25292f;
        font-size: 1rem;
        font-weight: 750;
    }

    .timeline-dot {
        width: 13px;
        height: 13px;
        border: 3px solid #4a515b;
        border-radius: 50%;
        background: white;
        flex: 0 0 13px;
        box-sizing: border-box;
    }

    .timeline-leg {
        border-left: 2px solid #d9dde3;
        margin-left: 5px;
        padding: 0.75rem 0 0.75rem 1.25rem;
    }

    .leg-title {
        color: #343a43;
        font-size: 0.95rem;
        font-weight: 700;
    }

    .leg-cost {
        color: #7b828d;
        font-size: 0.88rem;
        margin-top: 0.15rem;
    }

    .route-details {
        border-top: 1px solid #eef0f3;
        margin-top: 1rem;
        padding-top: 0.3rem;
    }

    .route-details summary {
        cursor: pointer;
        padding: 0.8rem 0;
        color: #343a43;
        font-weight: 600;
        min-height: 44px;
    }

    .route-details summary:focus-visible {
        outline: 2px solid #3478f6;
        outline-offset: 3px;
    }

    .route-details .detail-close { display: none; }
    .route-details[open] .detail-open { display: none; }
    .route-details[open] .detail-close { display: inline; }

    .card-bottom {
        border-top: 1px solid #eef0f3;
        margin-top: 0.9rem;
        padding-top: 0.9rem;
    }

    .card-message {
        color: #343a43;
        font-size: 0.95rem;
        font-weight: 650;
    }

    .budget-over {
        color: #a35b00;
        font-size: 0.88rem;
        font-weight: 700;
        margin-top: 0.45rem;
    }

    .friendly-notice {
        background: #fff8e8;
        border: 1px solid #f4dfac;
        border-radius: 16px;
        color: #5f4b21;
        line-height: 1.6;
        padding: 1rem 1.15rem;
        margin: 1.2rem 0;
    }

    .footnote {
        color: #89909a;
        font-size: 0.82rem;
        line-height: 1.55;
        margin-top: 0.8rem;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def show_notice(title, message):
    st.markdown(
        f"""
        <div class="friendly-notice">
            <strong>{title}</strong><br>
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def calculate_arrival_time(departure_time, total_time):
    departure = datetime.combine(datetime.today(), departure_time)
    arrival = departure + timedelta(minutes=total_time)
    days = (arrival.date() - departure.date()).days
    prefix = "다음 날 " if days == 1 else (f"{days}일 후 " if days > 1 else "")
    return prefix + arrival.strftime("%H:%M")


def valid_result(result):
    if not isinstance(result, dict):
        return False
    for key in ("save", "balance", "fast"):
        plan = result.get(key)
        if not isinstance(plan, dict):
            return False
        if plan.get("type") not in ("TRANSIT", "HYBRID", "TAXI"):
            return False
        for field in ("total_cost", "total_time", "subway_cost", "taxi_cost"):
            value = plan.get(field)
            if isinstance(value, bool) or not isinstance(value, Real):
                return False
            if not isfinite(value) or value < 0:
                return False
        if plan["type"] == "HYBRID" and not plan.get("station"):
            return False
    return True


def segment_time(plan, *keys):
    for key in keys:
        value = plan.get(key)
        if isinstance(value, Real) and not isinstance(value, bool) and isfinite(value) and value >= 0:
            return f" · {int(value)}분"
    return ""


def make_timeline(plan, start, destination):
    safe_start = escape(start)
    safe_destination = escape(destination)
    if plan.get("type") == "TRANSIT":
        transit_time = segment_time(plan, "subway_time")
        transit_cost = int(plan["subway_cost"])
        return f"""
        <div class="timeline">
            <div class="timeline-stop"><span class="timeline-dot"></span>{safe_start}</div>
            <div class="timeline-leg">
                <div class="leg-title">🚇 대중교통{transit_time}</div>
                <div class="leg-cost">{transit_cost:,}원 · 택시 이용 없음</div>
            </div>
            <div class="timeline-stop"><span class="timeline-dot"></span>{safe_destination}</div>
        </div>
        """
    taxi_cost = int(plan.get("taxi_cost", 0))
    taxi_time = segment_time(plan, "taxi_time", "taxi_minutes")

    if plan.get("type") == "TAXI":
        return f"""
        <div class="timeline">
            <div class="timeline-stop"><span class="timeline-dot"></span>{safe_start}</div>
            <div class="timeline-leg">
                <div class="leg-title">🚕 택시{taxi_time}</div>
                <div class="leg-cost">{taxi_cost:,}원</div>
            </div>
            <div class="timeline-stop"><span class="timeline-dot"></span>{safe_destination}</div>
        </div>
        """

    station = escape(str(plan.get("station", "환승 지점")))
    subway_cost = int(plan.get("subway_cost", 0))
    subway_time = segment_time(
        plan,
        "subway_time",
        "public_time",
        "transit_time",
        "subway_minutes",
    )

    return f"""
    <div class="timeline">
        <div class="timeline-stop"><span class="timeline-dot"></span>{safe_start}</div>
        <div class="timeline-leg">
            <div class="leg-title">🚇 대중교통{subway_time}</div>
            <div class="leg-cost">{subway_cost:,}원</div>
        </div>
        <div class="timeline-stop"><span class="timeline-dot"></span>{station}</div>
        <div class="timeline-leg">
            <div class="leg-title">🚕 택시{taxi_time}</div>
            <div class="leg-cost">{taxi_cost:,}원</div>
        </div>
        <div class="timeline-stop"><span class="timeline-dot"></span>{safe_destination}</div>
    </div>
    """


def make_comparison_message(plan, cheapest):
    """반환된 경로 중 최저 총요금 경로와 비용·시간을 비교한다."""
    if plan is cheapest:
        return "비교한 경로 중 가장 저렴해요."

    extra_cost = int(plan["total_cost"]) - int(cheapest["total_cost"])
    saved_time = int(cheapest["total_time"]) - int(plan["total_time"])

    if extra_cost == 0:
        if saved_time > 0:
            return f"같은 비용으로 {saved_time}분 빨라요."
        if saved_time < 0:
            return f"같은 비용으로 {-saved_time}분 더 걸려요."
        return "최저 비용 경로와 요금·소요시간이 같아요."

    if saved_time > 0:
        return (
            f"최저 비용 경로보다 {extra_cost:,}원 더 내고 "
            f"{saved_time}분 빨라요."
        )
    if saved_time < 0:
        return (
            f"최저 비용 경로보다 {extra_cost:,}원 더 들고, "
            f"{-saved_time}분 더 걸려요."
        )
    return f"최저 비용 경로와 소요시간은 같고, 비용은 {extra_cost:,}원 더 들어요."


def show_route_card(
    kind,
    emoji,
    plan,
    start,
    destination,
    departure_time,
    budget,
    message,
):
    total_cost = int(plan.get("total_cost", 0))
    total_time = int(plan.get("total_time", 0))
    taxi_cost = int(plan.get("taxi_cost", 0))
    arrival_time = calculate_arrival_time(departure_time, total_time)
    labels = {"save": "최저 비용", "balance": "예산 맞춤", "fast": "최단 시간"}
    description = labels[kind]
    if kind == "balance":
        description = (
            "예산 안에서 가장 빠른 경로"
            if taxi_cost <= budget else "예산 초과 · 최저 비용 대안"
        )
    route_type = {
        "TRANSIT": "대중교통만 이용",
        "HYBRID": "대중교통 + 택시",
        "TAXI": "택시 직행",
    }[plan["type"]]

    budget_message = ""
    if taxi_cost > budget:
        budget_message = (
            f'<div class="budget-over">택시 예산보다 '
            f'{taxi_cost - budget:,}원 더 필요해요.</div>'
        )

    st.markdown(
        f"""
        <div class="route-card {kind}">
            <div class="card-top">
                <div class="card-name">{emoji} {kind.upper()}</div>
                <div class="card-time">{total_time}분</div>
                <div class="card-price">총 {total_cost:,}원</div>
                <div class="card-arrival">{arrival_time} 도착 예정</div>
            </div>
            <div class="leg-title">{description}</div>
            <div class="leg-cost">{route_type} · 택시비 {taxi_cost:,}원 / 예산 {budget:,}원</div>
            <div class="card-bottom">
                <div class="card-message">💡 {message}</div>
                {budget_message}
            </div>
            <details class="route-details">
                <summary>
                    <span class="detail-open">상세 경로 보기</span>
                    <span class="detail-close">상세 경로 접기</span>
                </summary>
                {make_timeline(plan, start, destination)}
            </details>
        </div>
        """.replace("\n", ""),
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🏠 집갈각</div>
        <p class="hero-description">
            막차 걱정 없이, 대중교통과 택시를 조합해<br>
            예산에 맞는 귀가 방법을 찾아드려요.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("현재 MVP는 서울 지하철 2호선 본선 구간을 중심으로 지원합니다.")

with st.form("route_search_form"):
    start = st.text_input("📍 출발지", placeholder="예: 강남역")
    destination = st.text_input("🏠 도착지", placeholder="예: 홍대입구역")

    time_col, budget_col = st.columns(2)
    with time_col:
        departure_time = st.time_input("⏰ 출발 시간")
    with budget_col:
        budget = st.slider(
            "🚕 택시 예산",
            min_value=0,
            max_value=50000,
            value=11000,
            step=1000,
            format="%d원",
            help="택시에 사용할 수 있는 최대 금액을 입력하세요.",
        )

    submitted = st.form_submit_button(
        "집 가는 방법 찾기",
        use_container_width=True,
    )


if submitted:
    start = start.strip()
    destination = destination.strip()

    if not start or not destination:
        show_notice(
            "출발지와 도착지를 알려주세요 🙂",
            "두 장소를 모두 입력하면 귀가 방법을 바로 비교해드릴게요.",
        )
    elif start == destination:
        show_notice(
            "출발지와 도착지가 같아요",
            "도착지를 다시 확인한 뒤 검색해주세요.",
        )
    else:
        try:
            with st.spinner("귀가 경로와 예상 요금을 비교하고 있어요..."):
                result = get_recommendations(
                    start,
                    destination,
                    departure_time.strftime("%H:%M"),
                    int(budget),
                )
        except Exception as e:
            print("추천 계산 오류:", type(e).__name__)
            result = None
            request_failed = True
        else:
            request_failed = False

        if request_failed:
            show_notice(
                "지금은 경로를 불러오지 못했어요",
                "잠시 후 다시 눌러주세요. 입력한 장소와 예산은 그대로 유지됩니다.",
            )
        elif not result:
            show_notice(
                "조건에 맞는 귀가 경로를 찾지 못했어요",
                "출발지 이름을 조금 더 정확히 입력하거나 택시 예산을 높여 다시 찾아보세요.",
            )
        elif not valid_result(result):
            show_notice(
                "추천 경로를 완성하지 못했어요",
                "일부 교통 정보가 부족합니다. 잠시 후 다시 검색해주세요.",
            )
        else:
            plans = [result["save"], result["balance"], result["fast"]]
            cheapest = min(plans, key=lambda plan: int(plan["total_cost"]))
            safe_start = escape(start)
            safe_destination = escape(destination)
            all_over_budget = all(
                int(plan.get("taxi_cost", 0)) > int(budget) for plan in plans
            )

            if all_over_budget:
                show_notice(
                    "현재 예산 안의 경로는 없지만, 가까운 대안을 찾았어요",
                    "아래 경로별 추가 필요 금액을 확인하거나 택시 예산을 조정해보세요.",
                )

            st.markdown(
                f"""
                <div class="result-heading">
                    <h2>{safe_start} → {safe_destination}</h2>
                    <p>{departure_time.strftime('%H:%M')} 출발 · 택시 예산 {int(budget):,}원</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            show_route_card(
                "save",
                "💰",
                result["save"],
                start,
                destination,
                departure_time,
                int(budget),
                make_comparison_message(result["save"], cheapest),
            )
            show_route_card(
                "balance",
                "⚖️",
                result["balance"],
                start,
                destination,
                departure_time,
                int(budget),
                make_comparison_message(result["balance"], cheapest),
            )
            show_route_card(
                "fast",
                "⚡",
                result["fast"],
                start,
                destination,
                departure_time,
                int(budget),
                make_comparison_message(result["fast"], cheapest),
            )

            st.markdown(
                """
                <div class="footnote">
                    교통 상황과 호출 시점에 따라 실제 택시 요금 및 도착 시간은 달라질 수 있어요.
                    <br>막차 운행 판단에는 서울시 공공데이터를 활용하며,
                    이동 시간과 택시 요금 일부는 MVP 추정값입니다.
                </div>
                """,
                unsafe_allow_html=True,
            )
