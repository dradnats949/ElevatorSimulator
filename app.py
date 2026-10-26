import time

import pandas as pd
import streamlit as st

from algorithms import basic_algorithm, improved_algorithm
from compare_algorithms import generate_calls, run_simulation

FLOORS = 6
CAPACITY = 10
MOVE_DELAY = 0.6

st.set_page_config(page_title="AI Elevator Simulator", layout="wide")

if "elevators" not in st.session_state:
    st.session_state.elevators = [
        {"id": 1, "floor": 1, "direction": "정지", "passengers": 0},
        {"id": 2, "floor": 3, "direction": "정지", "passengers": 4},
        {"id": 3, "floor": 6, "direction": "정지", "passengers": 7},
    ]


def assign_elevator(start_floor):
    available = [e for e in st.session_state.elevators if e["passengers"] < CAPACITY]
    if not available:
        return None
    return min(available, key=lambda e: (abs(e["floor"] - start_floor), e["id"]))


def render_status():
    cols = st.columns(3)
    for col, elevator in zip(cols, st.session_state.elevators):
        with col:
            st.markdown(f"### {elevator['id']}번 엘리베이터")
            st.metric("현재 위치", f"{elevator['floor']}층")
            st.write(f"이동 방향: {elevator['direction']}")
            st.progress(
                elevator["passengers"] / CAPACITY,
                text=f"탑승 인원: {elevator['passengers']} / {CAPACITY}명",
            )


def render_building():
    header = st.columns([1, 2, 2, 2])
    for col, label in zip(header, ["층", "1번", "2번", "3번"]):
        col.markdown(f"**{label}**")
    for floor in range(FLOORS, 0, -1):
        cols = st.columns([1, 2, 2, 2])
        cols[0].write(f"**{floor}F**")
        for index, elevator in enumerate(st.session_state.elevators):
            if elevator["floor"] == floor:
                cols[index + 1].success(f"■ {elevator['id']}호기")
            else:
                cols[index + 1].write("─")


def refresh_visuals(status_box, building_box):
    with status_box.container():
        render_status()
    with building_box.container():
        render_building()


def move_elevator(elevator, target_floor, status_box, building_box):
    while elevator["floor"] != target_floor:
        if elevator["floor"] < target_floor:
            elevator["floor"] += 1
            elevator["direction"] = "상승"
        else:
            elevator["floor"] -= 1
            elevator["direction"] = "하강"
        refresh_visuals(status_box, building_box)
        time.sleep(MOVE_DELAY)
    elevator["direction"] = "정지"
    refresh_visuals(status_box, building_box)


st.title("AI Elevator Simulator")
st.caption("6층 건물 | 엘리베이터 3대 | 엘리베이터당 최대 정원 10명")
st.divider()

st.subheader("엘리베이터 호출")
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    start_floor = st.selectbox("현재 층", range(1, FLOORS + 1))
with col2:
    destination_floor = st.selectbox("목적층", range(1, FLOORS + 1), index=5)
with col3:
    st.write("")
    st.write("")
    assign_button = st.button("배정 및 운행 시작", use_container_width=True)

message_box = st.empty()
st.divider()
st.subheader("엘리베이터 운행 현황")
status_box = st.empty()
st.divider()
st.subheader("6층 건물 시뮬레이션")
building_box = st.empty()
refresh_visuals(status_box, building_box)

if assign_button:
    if start_floor == destination_floor:
        message_box.warning("현재 층과 목적층이 같습니다.")
    else:
        selected = assign_elevator(start_floor)
        if selected is None:
            message_box.error("모든 엘리베이터가 정원에 도달했습니다.")
        else:
            message_box.info(f"{selected['id']}번 엘리베이터 배정! {start_floor}층으로 이동합니다.")
            move_elevator(selected, start_floor, status_box, building_box)
            selected["passengers"] += 1
            message_box.success(f"{selected['id']}번 엘리베이터 도착! 탑승 후 {destination_floor}층으로 이동합니다.")
            refresh_visuals(status_box, building_box)
            time.sleep(0.8)
            move_elevator(selected, destination_floor, status_box, building_box)
            selected["passengers"] -= 1
            refresh_visuals(status_box, building_box)
            message_box.success(f"{selected['id']}번 엘리베이터가 {destination_floor}층에 도착했습니다. 운행 완료!")

st.divider()
st.subheader("알고리즘 성능 비교")
st.markdown("### 시뮬레이션 조건 설정")
passenger_count = st.slider("가상 이용자 수", min_value=10, max_value=100, value=50, step=10)
scenario = st.radio(
    "호출 유형",
    options=["random", "morning", "lunch"],
    format_func=lambda x: {
        "random": "일반 시간대", "morning": "등교 시간대", "lunch": "점심 시간대"
    }[x],
    horizontal=True,
)
st.caption("등교·점심 시간대의 호출 집중 비율은 실제 측정값이 아닌 가상 설정입니다.")

if st.button("알고리즘 성능 비교 실행"):
    calls = generate_calls(count=passenger_count, seed=42, scenario=scenario)
    with st.spinner("동일한 가상 호출 데이터로 두 알고리즘을 실행하고 있습니다..."):
        basic = run_simulation(calls, basic_algorithm)
        improved = run_simulation(calls, improved_algorithm)

    if basic is None or improved is None:
        st.error("시뮬레이션 결과를 계산할 수 없습니다.")
    else:
        st.write(f"기존 알고리즘 완료: {basic['completed']}/{basic['total']}명")
        st.write(f"개선 알고리즘 완료: {improved['completed']}/{improved['total']}명")
        if basic["completed"] == basic["total"] and improved["completed"] == improved["total"]:
            baseline = basic["average_wait"]
            reduction = ((baseline - improved["average_wait"]) / baseline * 100) if baseline > 0 else 0.0
            metric1, metric2, metric3 = st.columns(3)
            metric1.metric("기존 평균 대기시간", f"{baseline:.2f}초")
            metric2.metric("개선 평균 대기시간", f"{improved['average_wait']:.2f}초")
            metric3.metric("평균 대기시간 감소율", f"{reduction:.2f}%")

            chart_data = pd.DataFrame({
                "알고리즘": ["기존", "개선"],
                "평균 대기시간(초)": [basic["average_wait"], improved["average_wait"]],
            })
            st.bar_chart(chart_data, x="알고리즘", y="평균 대기시간(초)")

            comparison = pd.DataFrame({
                "항목": ["평균 대기시간(초)", "총 대기시간(초)", "평균 이동시간(초)"],
                "기존": [basic["average_wait"], basic["total_wait"], basic["average_travel"]],
                "개선": [improved["average_wait"], improved["total_wait"], improved["average_travel"]],
            })
            st.dataframe(comparison, hide_index=True, use_container_width=True)
            st.caption("현재 결과는 개발 중인 가상 시뮬레이터의 예비 결과입니다. 개선 방식은 학습형 AI가 아닌 예상 도착시간 기반 알고리즘입니다.")
        else:
            st.warning("미완료 이용자가 있어 평균 대기시간 감소율을 표시하지 않습니다.")


# ==========================================
# 상세 시뮬레이션 결과
# ==========================================
        if (
            basic is not None
            and improved is not None
            and basic["completed"] == basic["total"]
            and improved["completed"] == improved["total"]
        ):
            st.divider()
            st.subheader("상세 시뮬레이션 결과")

            # 가상 호출 데이터
            st.markdown("#### 1. 가상 호출 데이터")

            calls_df = pd.DataFrame(
                calls,
                columns=[
                    "이용자 번호",
                    "호출 시각(초)",
                    "출발층",
                    "목적층"
                ]
            )

            st.dataframe(
                calls_df,
                hide_index=True,
                use_container_width=True
            )

            # 알고리즘별 결과
            st.markdown("#### 2. 알고리즘별 이용자 결과")

            basic_df = pd.DataFrame(
                basic["passenger_results"]
            )

            improved_df = pd.DataFrame(
                improved["passenger_results"]
            )

            result_df = pd.DataFrame({
                "이용자 번호": basic_df["id"],
                "출발층": basic_df["start_floor"],
                "목적층": basic_df["destination_floor"],
                "기존 배정": basic_df["elevator"],
                "개선 배정": improved_df["elevator"],
                "기존 대기시간(초)": basic_df["waiting_time"],
                "개선 대기시간(초)": improved_df["waiting_time"],
                "대기시간 차이(초)": (
                    basic_df["waiting_time"]
                    - improved_df["waiting_time"]
                ),
                "기존 이동시간(초)": basic_df["travel_time"],
                "개선 이동시간(초)": improved_df["travel_time"]
            })

            st.dataframe(
                result_df,
                hide_index=True,
                use_container_width=True
            )

            st.caption(
                "대기시간 차이가 양수이면 개선 알고리즘에서 "
                "대기시간이 단축된 이용자입니다."
            )

            # 최대 대기시간 비교
            st.markdown("#### 3. 최대 대기시간 비교")

            col1, col2 = st.columns(2)

            col1.metric(
                "기존 최대 대기시간",
                f"{basic['max_wait']:.0f}초"
            )

            col2.metric(
                "개선 최대 대기시간",
                f"{improved['max_wait']:.0f}초"
            )

            # CSV 다운로드
            st.markdown("#### 4. 결과 다운로드")

            csv_data = result_df.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                label="이용자별 비교 결과 CSV 다운로드",
                data=csv_data,
                file_name="elevator_comparison.csv",
                mime="text/csv"
            )


# ==========================================
# 30회 반복 실험 결과 시각화
# ==========================================
st.divider()
st.subheader("반복 시뮬레이션 성능 분석")

from compare_algorithms import run_repeated_comparison

repetition_count = st.slider(
    "반복 실험 횟수",
    min_value=10,
    max_value=100,
    value=30,
    step=10
)

if st.button("반복 실험 실행"):
    with st.spinner("반복 실험을 진행하고 있습니다..."):
        results = run_repeated_comparison(
            repetitions=repetition_count,
            passenger_count=passenger_count,
            scenario=scenario
        )

    repeated_df = pd.DataFrame(results)

    basic_average = repeated_df["basic_wait"].mean()
    improved_average = repeated_df["improved_wait"].mean()

    reduction = (
        (basic_average - improved_average)
        / basic_average * 100
        if basic_average > 0 else 0
    )

    wins = (
        repeated_df["improved_wait"]
        < repeated_df["basic_wait"]
    ).sum()

    st.markdown("#### 반복 실험 종합 결과")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "기존 평균 대기시간",
        f"{basic_average:.2f}초"
    )

    col2.metric(
        "개선 평균 대기시간",
        f"{improved_average:.2f}초"
    )

    col3.metric(
        "평균 대기시간 감소율",
        f"{reduction:.2f}%"
    )

    st.metric(
        "개선 알고리즘 우수 횟수",
        f"{wins}/{repetition_count}회",
        f"{wins / repetition_count * 100:.1f}%"
    )

    st.markdown("#### 실험별 평균 대기시간")

    chart_df = repeated_df.rename(columns={
        "experiment": "실험 회차",
        "basic_wait": "기존 알고리즘",
        "improved_wait": "개선 알고리즘"
    })

    st.line_chart(
        chart_df.set_index("실험 회차")[
            ["기존 알고리즘", "개선 알고리즘"]
        ]
    )

    st.markdown("#### 실험별 대기시간 감소율")

    reduction_df = repeated_df.rename(columns={
        "experiment": "실험 회차",
        "reduction": "감소율(%)"
    })

    st.bar_chart(
        reduction_df,
        x="실험 회차",
        y="감소율(%)"
    )

    st.markdown("#### 반복 실험 상세 데이터")

    st.dataframe(
        repeated_df.rename(columns={
            "experiment": "실험 회차",
            "basic_wait": "기존 평균 대기시간(초)",
            "improved_wait": "개선 평균 대기시간(초)",
            "reduction": "감소율(%)"
        }),
        hide_index=True,
        use_container_width=True
    )


# ==========================================
# 시간대별 알고리즘 성능 비교
# ==========================================
st.divider()
st.subheader("시간대별 알고리즘 성능 비교")

st.caption(
    "일반·등교·점심 시간대에 동일한 실험 조건을 적용하여 "
    "알고리즘 성능을 비교합니다."
)

if st.button("전체 시간대 비교 실행"):

    scenarios = {
        "일반 시간대": "random",
        "등교 시간대": "morning",
        "점심 시간대": "lunch"
    }

    summary = []

    with st.spinner("시간대별 반복 실험을 진행하고 있습니다..."):

        for name, scenario_code in scenarios.items():

            results = run_repeated_comparison(
                repetitions=repetition_count,
                passenger_count=passenger_count,
                scenario=scenario_code
            )

            basic_average = sum(
                r["basic_wait"] for r in results
            ) / len(results)

            improved_average = sum(
                r["improved_wait"] for r in results
            ) / len(results)

            reduction = (
                (basic_average - improved_average)
                / basic_average * 100
                if basic_average > 0 else 0
            )

            wins = sum(
                r["improved_wait"] < r["basic_wait"]
                for r in results
            )

            summary.append({
                "시간대": name,
                "기존 평균 대기시간(초)": basic_average,
                "개선 평균 대기시간(초)": improved_average,
                "대기시간 감소율(%)": reduction,
                "개선 우수 횟수": wins
            })

    summary_df = pd.DataFrame(summary)

    st.markdown("#### 시간대별 종합 결과")

    st.dataframe(
        summary_df,
        hide_index=True,
        use_container_width=True
    )

    st.markdown("#### 시간대별 평균 대기시간")

    st.bar_chart(
        summary_df,
        x="시간대",
        y=[
            "기존 평균 대기시간(초)",
            "개선 평균 대기시간(초)"
        ]
    )

    st.markdown("#### 시간대별 개선율")

    st.bar_chart(
        summary_df,
        x="시간대",
        y="대기시간 감소율(%)"
    )

    best = summary_df.loc[
        summary_df["대기시간 감소율(%)"].idxmax()
    ]

    st.success(
        f"개선율이 가장 높은 조건은 "
        f"{best['시간대']}이며, "
        f"평균 대기시간이 "
        f"{best['대기시간 감소율(%)']:.2f}% 감소했습니다."
    )


# ==========================================
# 엘리베이터 운행 애니메이션 비교
# ==========================================
import time
from visual_simulation import create_comparison_history

st.divider()
st.subheader("엘리베이터 운행 시뮬레이션")

st.caption(
    "학생 20명이 0~120초 사이에 1층에 도착하여 "
    "2~6층 중 무작위 목적층으로 이동하는 상황입니다."
)

animation_speed = st.select_slider(
    "재생 속도",
    options=[1, 2, 5, 10, 20],
    value=5,
    format_func=lambda x: f"{x}배속"
)

if st.button("운행 시뮬레이션 시작"):

    basic_visual, improved_visual = create_comparison_history(
        count=20,
        seed=42
    )

    basic_history = basic_visual["history"]
    improved_history = improved_visual["history"]

    max_frames = max(
        len(basic_history),
        len(improved_history)
    )

    # 화면이 갱신될 영역
    animation_area = st.empty()

    for frame in range(max_frames):

        basic_state = basic_history[
            min(frame, len(basic_history) - 1)
        ]

        improved_state = improved_history[
            min(frame, len(improved_history) - 1)
        ]

        with animation_area.container():

            st.markdown(f"### 시뮬레이션 시간: {frame}초")

            col1, col2 = st.columns(2)

            for col, title, state in [
                (col1, "기존 알고리즘", basic_state),
                (col2, "개선 알고리즘", improved_state)
            ]:

                with col:
                    st.markdown(f"#### {title}")

                    st.metric(
                        "목적층 도착",
                        f"{state['completed']}/20명"
                    )

                    st.metric(
                        "엘리베이터 대기",
                        f"{state['waiting']}명"
                    )

                    # 엘리베이터 위치를 표로 표시
                    elevator_data = []

                    for elevator in state["elevators"]:
                        elevator_data.append({
                            "엘리베이터": elevator["id"],
                            "현재 층": elevator["floor"],
                            "이동 방향": elevator["direction"],
                            "탑승 인원": elevator["passengers"]
                        })

                    st.dataframe(
                        elevator_data,
                        hide_index=True,
                        use_container_width=True
                    )

                    # 층별 엘리베이터 위치
                    for floor in range(6, 0, -1):

                        elevator_positions = []

                        for elevator in state["elevators"]:
                            if elevator["floor"] == floor:
                                elevator_positions.append(
                                    f"🛗 {elevator['id']}호기"
                                )

                        position_text = (
                            " | ".join(elevator_positions)
                            if elevator_positions
                            else "　"
                        )

                        st.markdown(
                            f"**{floor}층**　│　{position_text}"
                        )

        time.sleep(1 / animation_speed)
    
    # ==========================================
    # 운행 완료 후 결과 그래프
    # ==========================================
    st.divider()
    st.subheader("운행 시뮬레이션 결과")

    if (
        basic_visual["completed"] == 20
        and improved_visual["completed"] == 20
    ):
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "기존 평균 대기시간",
                f"{basic_visual['average_wait']:.2f}초"
            )

        with col2:
            st.metric(
                "개선 평균 대기시간",
                f"{improved_visual['average_wait']:.2f}초"
            )

        wait_reduction = (
            (
                basic_visual["average_wait"]
                - improved_visual["average_wait"]
            )
            / basic_visual["average_wait"] * 100
            if basic_visual["average_wait"] > 0
            else 0
        )

        st.metric(
            "평균 대기시간 감소율",
            f"{wait_reduction:.2f}%"
        )

        # 평균 대기시간 비교 그래프
        st.markdown("#### 평균 대기시간 비교")

        wait_chart = pd.DataFrame({
            "알고리즘": ["기존", "개선"],
            "평균 대기시간(초)": [
                basic_visual["average_wait"],
                improved_visual["average_wait"]
            ]
        })

        st.bar_chart(
            wait_chart,
            x="알고리즘",
            y="평균 대기시간(초)"
        )

        # 전체 이동 완료 시간 비교
        st.markdown("#### 전체 학생 이동 완료 시간")

        finish_chart = pd.DataFrame({
            "알고리즘": ["기존", "개선"],
            "완료 시간(초)": [
                basic_visual["finish_time"],
                improved_visual["finish_time"]
            ]
        })

        st.bar_chart(
            finish_chart,
            x="알고리즘",
            y="완료 시간(초)"
        )

        # 결과 요약
        st.markdown("#### 최종 결과")

        if wait_reduction > 0:
            st.success(
                f"개선 알고리즘을 적용했을 때 "
                f"평균 대기시간이 {wait_reduction:.2f}% 감소했습니다."
            )
        elif wait_reduction < 0:
            st.warning(
                f"이번 시뮬레이션에서는 개선 알고리즘의 "
                f"평균 대기시간이 {-wait_reduction:.2f}% 증가했습니다."
            )
        else:
            st.info(
                "두 알고리즘의 평균 대기시간이 동일합니다."
            )

    else:
        st.warning(
            "모든 학생이 이동을 완료하지 않아 "
            "결과를 비교할 수 없습니다."
        )

