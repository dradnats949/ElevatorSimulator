
FLOORS = 6
CAPACITY = 10

FLOOR_TRAVEL_TIME = 3
STOP_TIME = 5


class Passenger:
    def __init__(self, passenger_id, call_time, start_floor, destination_floor):
        if not 1 <= start_floor <= FLOORS:
            raise ValueError("출발층이 올바르지 않습니다.")
        if not 1 <= destination_floor <= FLOORS:
            raise ValueError("목적층이 올바르지 않습니다.")
        if start_floor == destination_floor:
            raise ValueError("출발층과 목적층이 같습니다.")
        if call_time < 0:
            raise ValueError("호출 시각은 0 이상이어야 합니다.")

        self.id = passenger_id
        self.call_time = call_time
        self.start_floor = start_floor
        self.destination_floor = destination_floor

        self.board_time = None
        self.arrival_time = None
        self.assigned_elevator = None

    def waiting_time(self):
        if self.board_time is None:
            return None
        return self.board_time - self.call_time

    def travel_time(self):
        if self.arrival_time is None:
            return None
        return self.arrival_time - self.board_time


class Elevator:
    def __init__(self, elevator_id, initial_floor=1):
        self.id = elevator_id
        self.floor = initial_floor
        self.direction = "정지"

        self.passengers = []
        self.waiting_passengers = []
        self.target_floors = []

        self.timer = 0
        self.state = "idle"
        self.next_floor = None

    def passenger_count(self):
        return len(self.passengers)

    def has_capacity(self):
        # 기존 탑승자와 배정된 대기자를 함께 고려
        return (
            len(self.passengers) + len(self.waiting_passengers)
            < CAPACITY
        )

    def add_target(self, floor):
        if floor not in self.target_floors:
            self.target_floors.append(floor)

    def add_passenger_request(self, passenger):
        self.waiting_passengers.append(passenger)
        self.add_target(passenger.start_floor)

    def process_stop(self, current_time):
        # 하차 처리
        remaining = []

        for passenger in self.passengers:
            if passenger.destination_floor == self.floor:
                passenger.arrival_time = current_time
            else:
                remaining.append(passenger)

        self.passengers = remaining

        # 탑승 처리
        still_waiting = []

        for passenger in self.waiting_passengers:
            if (
                passenger.start_floor == self.floor
                and len(self.passengers) < CAPACITY
            ):
                passenger.board_time = current_time
                self.passengers.append(passenger)
                self.add_target(passenger.destination_floor)
            else:
                still_waiting.append(passenger)

        self.waiting_passengers = still_waiting

    def step(self, current_time):
        # 이동 또는 정차 중인 경우
        if self.timer > 0:
            self.timer -= 1

            if self.timer == 0:
                if self.state == "moving":
                    self.floor = self.next_floor
                    self.next_floor = None

                elif self.state == "stopped":
                    self.process_stop(current_time)
                    self.state = "idle"

            return

        if not self.target_floors:
            self.state = "idle"
            self.direction = "정지"
            return

        target = self.target_floors[0]

        # 목적층 도착
        if self.floor == target:
            self.target_floors.pop(0)
            self.state = "stopped"
            self.direction = "정지"
            self.timer = STOP_TIME
            return

        # 한 층 이동 시작
        self.state = "moving"

        if self.floor < target:
            self.direction = "상승"
            self.next_floor = self.floor + 1
        else:
            self.direction = "하강"
            self.next_floor = self.floor - 1

        self.timer = FLOOR_TRAVEL_TIME

    def get_status(self):
        return {
            "id": self.id,
            "floor": self.floor,
            "direction": self.direction,
            "passengers": self.passenger_count(),
            "targets": self.target_floors.copy(),
            "state": self.state
        }


class ElevatorSimulator:
    def __init__(self):
        self.elevators = [
            Elevator(1, 1),
            Elevator(2, 3),
            Elevator(3, 6)
        ]

        self.passengers = []
        self.current_time = 0

    def add_passenger(self, passenger):
        self.passengers.append(passenger)

    
    def assign_passenger(self, passenger, algorithm=None):
        if algorithm is None:
            available = [
                e for e in self.elevators
                if e.has_capacity()
            ]

            if not available:
                return None

            selected = min(
                available,
                key=lambda e: (
                    abs(e.floor - passenger.start_floor),
                    e.id
                )
            )
        else:
            selected = algorithm(
                self.elevators,
                passenger
            )

        if selected is None:
            return None

        passenger.assigned_elevator = selected.id
        selected.add_passenger_request(passenger)

        return selected


    def step(self):
        self.current_time += 1

        for elevator in self.elevators:
            elevator.step(self.current_time)

    def get_status(self):
        return [
            elevator.get_status()
            for elevator in self.elevators
        ]

    def get_results(self):
        return [
            {
                "id": p.id,
                "elevator": p.assigned_elevator,
                "waiting_time": p.waiting_time(),
                "travel_time": p.travel_time()
            }
            for p in self.passengers
        ]
