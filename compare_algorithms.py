
import random

from simulator import ElevatorSimulator, Passenger
from algorithms import basic_algorithm, improved_algorithm


# ==========================================
# 가상 호출 데이터 생성
# ==========================================

def generate_calls(count=50, seed=42, scenario="random"):
    rng = random.Random(seed)
    calls = []

    for i in range(count):
        # 호출 시간: 0~300초
        call_time = rng.randint(0, 300)

        if scenario == "morning":
            # 등교: 1층에서 상층부로 이동하는 호출 80%
            if rng.random() < 0.8:
                start_floor = 1
                destination_floor = rng.randint(2, 6)
            else:
                start_floor = rng.randint(2, 6)
                destination_floor = rng.choice(
                    [f for f in range(1, 7) if f != start_floor]
                )

        elif scenario == "lunch":
            # 점심: 상층부에서 1층으로 이동하는 호출 80%
            if rng.random() < 0.8:
                start_floor = rng.randint(2, 6)
                destination_floor = 1
            else:
                start_floor = rng.randint(1, 6)
                destination_floor = rng.choice(
                    [f for f in range(1, 7) if f != start_floor]
                )

        else:
            # 일반: 층별 무작위 호출
            start_floor = rng.randint(1, 6)
            destination_floor = rng.choice(
                [f for f in range(1, 7) if f != start_floor]
            )

        calls.append((
            i + 1,
            call_time,
            start_floor,
            destination_floor
        ))

    return sorted(calls, key=lambda x: (x[1], x[0]))


# ==========================================
# 알고리즘별 시뮬레이션
# ==========================================
def run_simulation(calls, algorithm):
    sim = ElevatorSimulator()

    passengers = [
        Passenger(*call)
        for call in calls
    ]

    for passenger in passengers:
        sim.add_passenger(passenger)

    pending = passengers.copy()
    max_time = 3600

    while sim.current_time < max_time:

        # 호출 시각이 된 이용자 배정
        still_pending = []

        for passenger in pending:
            if passenger.call_time <= sim.current_time:
                if passenger.assigned_elevator is None:
                    sim.assign_passenger(
                        passenger,
                        algorithm
                    )

                if passenger.assigned_elevator is None:
                    still_pending.append(passenger)
            else:
                still_pending.append(passenger)

        pending = still_pending

        # 모든 이용자가 도착하면 종료
        if all(
            p.arrival_time is not None
            for p in passengers
        ):
            break

        sim.step()

    completed = [
        p for p in passengers
        if p.arrival_time is not None
    ]

    if not completed:
        return None

    average_wait = sum(
        p.waiting_time()
        for p in completed
    ) / len(completed)

    total_wait = sum(
        p.waiting_time()
        for p in completed
    )

    average_travel = sum(
        p.travel_time()
        for p in completed
    ) / len(completed)

    
    return {
        "completed": len(completed),
        "total": len(passengers),
        "average_wait": average_wait,
        "total_wait": total_wait,
        "average_travel": average_travel,
        "max_wait": max(p.waiting_time() for p in completed),

        "passenger_results": [
            {
                "id": p.id,
                "call_time": p.call_time,
                "start_floor": p.start_floor,
                "destination_floor": p.destination_floor,
                "elevator": p.assigned_elevator,
                "board_time": p.board_time,
                "arrival_time": p.arrival_time,
                "waiting_time": p.waiting_time(),
                "travel_time": p.travel_time()
            }
            for p in passengers
        ]
    }



# ==========================================
# 직접 실행할 때만 성능 비교
# ==========================================
if __name__ == "__main__":

    calls = generate_calls(count=50, seed=42)

    basic = run_simulation(
        calls,
        basic_algorithm
    )

    improved = run_simulation(
        calls,
        improved_algorithm
    )

    print("===== 알고리즘 성능 비교 =====")

    if basic is None or improved is None:
        print("시뮬레이션 결과를 계산할 수 없습니다.")

    else:
        print("\n[기존 알고리즘]")
        print(f"완료: {basic['completed']}/{basic['total']}명")
        print(f"평균 대기시간: {basic['average_wait']:.2f}초")
        print(f"총 대기시간: {basic['total_wait']:.2f}초")
        print(f"평균 이동시간: {basic['average_travel']:.2f}초")

        print("\n[개선 알고리즘]")
        print(f"완료: {improved['completed']}/{improved['total']}명")
        print(f"평균 대기시간: {improved['average_wait']:.2f}초")
        print(f"총 대기시간: {improved['total_wait']:.2f}초")
        print(f"평균 이동시간: {improved['average_travel']:.2f}초")

        if (
            basic["completed"] == basic["total"]
            and improved["completed"] == improved["total"]
        ):
            reduction = (
                (basic["average_wait"] - improved["average_wait"])
                / basic["average_wait"] * 100
            ) if basic["average_wait"] > 0 else 0

            print(
                f"\n평균 대기시간 감소율: {reduction:.2f}%"
            )
        else:
            print(
                "\n미완료 이용자가 있어 감소율을 계산하지 않습니다."
            )


# ==========================================
# 반복 시뮬레이션 성능 비교
# ==========================================
def run_repeated_comparison(
    repetitions=30,
    passenger_count=50,
    scenario="random"
):
    results = []

    for i in range(repetitions):
        # 매 실험마다 다른 호출 데이터 생성
        calls = generate_calls(
            count=passenger_count,
            seed=42 + i,
            scenario=scenario
        )

        # 두 알고리즘에 동일한 호출 데이터 적용
        basic = run_simulation(
            calls,
            basic_algorithm
        )

        improved = run_simulation(
            calls,
            improved_algorithm
        )

        # 모든 이용자가 이동을 완료한 경우만 기록
        if (
            basic is None
            or improved is None
            or basic["completed"] != basic["total"]
            or improved["completed"] != improved["total"]
        ):
            raise RuntimeError(
                f"{i + 1}회차 시뮬레이션이 완료되지 않았습니다."
            )

        reduction = (
            (basic["average_wait"] - improved["average_wait"])
            / basic["average_wait"] * 100
            if basic["average_wait"] > 0
            else 0
        )

        results.append({
            "experiment": i + 1,
            "basic_wait": basic["average_wait"],
            "improved_wait": improved["average_wait"],
            "reduction": reduction
        })

    return results


