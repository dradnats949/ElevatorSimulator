
import random

from simulator import ElevatorSimulator, Passenger
from algorithms import basic_algorithm, improved_algorithm


# ==========================================
# 20명의 학생 호출 데이터 생성
# ==========================================
def generate_student_calls(count=20, seed=42):
    rng = random.Random(seed)
    calls = []

    for i in range(count):
        call_time = rng.randint(0, 120)
        destination = rng.randint(2, 6)

        calls.append((
            i + 1,
            call_time,
            1,
            destination
        ))

    return sorted(calls, key=lambda x: (x[1], x[0]))


# ==========================================
# 매초 엘리베이터 운행 상태 기록
# ==========================================
def record_simulation(calls, algorithm):
    sim = ElevatorSimulator()

    passengers = [
        Passenger(*call)
        for call in calls
    ]

    for passenger in passengers:
        sim.add_passenger(passenger)

    pending = passengers.copy()
    history = []

    max_time = 3600

    while sim.current_time < max_time:

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

        # 현재 상태 기록
        elevator_states = []

        for elevator in sim.elevators:
            elevator_states.append({
                "id": elevator.id,
                "floor": elevator.floor,
                "direction": elevator.direction,
                "state": elevator.state,
                "passengers": len(elevator.passengers),
                "waiting_pickups": len(
                    elevator.waiting_passengers
                )
            })

        waiting_count = sum(
            1
            for p in passengers
            if (
                p.call_time <= sim.current_time
                and p.board_time is None
            )
        )

        completed_count = sum(
            1
            for p in passengers
            if p.arrival_time is not None
        )

        history.append({
            "time": sim.current_time,
            "elevators": elevator_states,
            "waiting": waiting_count,
            "completed": completed_count
        })

        if completed_count == len(passengers):
            break

        sim.step()

    
    completed_passengers = [
        p for p in passengers
        if p.arrival_time is not None
    ]

    average_wait = (
        sum(p.waiting_time() for p in completed_passengers)
        / len(completed_passengers)
        if completed_passengers else 0
    )

    average_travel = (
        sum(p.travel_time() for p in completed_passengers)
        / len(completed_passengers)
        if completed_passengers else 0
    )

    
    completed_passengers = [
        p for p in passengers
        if p.arrival_time is not None
    ]

    average_wait = (
        sum(p.waiting_time() for p in completed_passengers)
        / len(completed_passengers)
        if completed_passengers else 0
    )

    average_travel = (
        sum(p.travel_time() for p in completed_passengers)
        / len(completed_passengers)
        if completed_passengers else 0
    )

    return {
        "history": history,
        "calls": calls,
        "completed": len(completed_passengers),
        "total": len(passengers),
        "average_wait": average_wait,
        "average_travel": average_travel,
        "finish_time": max(
            (p.arrival_time for p in completed_passengers),
            default=0
        )
    }




# ==========================================
# 두 알고리즘 비교용 기록 생성
# ==========================================
def create_comparison_history(count=20, seed=42):
    calls = generate_student_calls(
        count=count,
        seed=seed
    )

    basic = record_simulation(
        calls,
        basic_algorithm
    )

    improved = record_simulation(
        calls,
        improved_algorithm
    )

    return basic, improved
