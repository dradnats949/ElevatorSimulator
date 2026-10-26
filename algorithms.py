
from simulator import FLOOR_TRAVEL_TIME, STOP_TIME


# ==========================================
# 1. 기존 배정 알고리즘
# ==========================================
def basic_algorithm(elevators, passenger):

    available = [
        e for e in elevators
        if e.has_capacity()
    ]

    if not available:
        return None

    # 호출층과 가장 가까운 엘리베이터 선택
    selected = min(
        available,
        key=lambda e: (
            abs(e.floor - passenger.start_floor),
            e.id
        )
    )

    return selected


# ==========================================
# 2. 예상 도착시간 계산
# ==========================================
def estimate_arrival_time(elevator, start_floor):

    current_floor = elevator.floor
    targets = elevator.target_floors.copy()

    estimated_time = 0

    # 현재 진행 중인 동작의 남은 시간
    if elevator.timer > 0:
        estimated_time += elevator.timer

        if elevator.state == "moving":
            current_floor = elevator.next_floor

    # 기존 정차 요청 처리 시간 추정
    for target in targets:
        distance = abs(target - current_floor)

        estimated_time += (
            distance * FLOOR_TRAVEL_TIME
        )

        estimated_time += STOP_TIME
        current_floor = target

    # 기존 요청 처리 후 호출층까지 이동
    distance_to_passenger = abs(
        start_floor - current_floor
    )

    estimated_time += (
        distance_to_passenger * FLOOR_TRAVEL_TIME
    )

    return estimated_time


# ==========================================
# 3. 개선된 배정 알고리즘
# ==========================================
def improved_algorithm(elevators, passenger):

    available = [
        e for e in elevators
        if e.has_capacity()
    ]

    if not available:
        return None

    # 예상 도착시간이 가장 짧은 엘리베이터 선택
    selected = min(
        available,
        key=lambda e: (
            estimate_arrival_time(
                e,
                passenger.start_floor
            ),
            e.id
        )
    )

    return selected
