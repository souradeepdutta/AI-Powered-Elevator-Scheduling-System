import heapq
import threading
import time
import pygame

# Get user input for number of floors and elevators
num_floors = int(input("Enter the number of floors: "))
num_elevators = int(input("Enter the number of elevators: "))

# Pygame settings (Scalable window height)
WIDTH, BASE_HEIGHT = 400, 600
HEIGHT = max(BASE_HEIGHT, num_floors * 50)  # Scale height dynamically
ELEVATOR_WIDTH, ELEVATOR_HEIGHT = 40, 50
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)

# Generate distinct colors for each elevator
ELEVATOR_COLORS = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100),
                    (255, 100, 255), (100, 255, 255), (200, 150, 100), (150, 100, 200)]
ELEVATOR_COLORS *= (num_elevators // len(ELEVATOR_COLORS)) + 1  # Repeat if needed

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elevator Simulation")
clock = pygame.time.Clock()

class Elevator:
    def __init__(self, id, floors):
        self.id = id
        self.current_floor = 1
        self.direction = 0  # 1 = Up, -1 = Down, 0 = Idle
        self.hall_calls = []  # Requests from outside
        self.cab_calls = []   # Requests from inside
        self.lock = threading.Lock()

    def add_hall_call(self, floor):
        with self.lock:
            if floor not in self.hall_calls:
                heapq.heappush(self.hall_calls, floor)

    def add_cab_call(self, floor):
        with self.lock:
            if floor not in self.cab_calls:
                heapq.heappush(self.cab_calls, floor)

    def move(self):
        while True:
            with self.lock:
                target_floor = None
                if self.hall_calls:
                    target_floor = heapq.heappop(self.hall_calls)
                elif self.cab_calls:
                    target_floor = heapq.heappop(self.cab_calls)

            if target_floor:
                self.direction = 1 if target_floor > self.current_floor else -1
                while self.current_floor != target_floor:
                    time.sleep(0.5)
                    self.current_floor += self.direction
                    update_visualization()

                print(f"🚪 Elevator {self.id} arrived at Floor {self.current_floor}")

                with self.lock:
                    if not self.hall_calls and not self.cab_calls:
                        self.direction = 0
            else:
                time.sleep(0.2)

def calculate_heuristic(elevator, source):
    return abs(elevator.current_floor - source)

class ElevatorSystem:
    def __init__(self, num_elevators, num_floors):
        self.elevators = [Elevator(i+1, num_floors) for i in range(num_elevators)]
        self.lock = threading.Lock()

    def find_best_elevator(self, source):
        return min(self.elevators, key=lambda e: calculate_heuristic(e, source))

    def request_elevator(self, source, destination):
        with self.lock:
            best_elevator = self.find_best_elevator(source)
            best_elevator.add_hall_call(source)
            print(f"✅ Elevator {best_elevator.id} is coming to Floor {source}")
            time.sleep(1)
            best_elevator.add_cab_call(destination)
            print(f"✅ Elevator {best_elevator.id} will take you to Floor {destination}")

    def start_system(self):
        for elevator in self.elevators:
            threading.Thread(target=elevator.move, daemon=True).start()

def update_visualization():
    screen.fill(BACKGROUND_COLOR)
    elevator_spacing = WIDTH // (num_elevators + 1)

    for i, elevator in enumerate(system.elevators):
        x = (i + 1) * elevator_spacing - ELEVATOR_WIDTH // 2
        y = HEIGHT - (elevator.current_floor / num_floors) * (HEIGHT - ELEVATOR_HEIGHT - 25) - ELEVATOR_HEIGHT
        pygame.draw.rect(screen, ELEVATOR_COLORS[i], (x, y, ELEVATOR_WIDTH, ELEVATOR_HEIGHT))
        font = pygame.font.Font(None, 24)
        text = font.render(f"E{i+1}: {elevator.current_floor}", True, TEXT_COLOR)
        screen.blit(text, (x, y - 20))

    pygame.display.flip()
    clock.tick(30)

def main():
    global system
    system = ElevatorSystem(num_elevators, num_floors)
    system.start_system()

    request_thread = threading.Thread(target=request_input, daemon=True)
    request_thread.start()

    while True:
        update_visualization()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

def request_input():
    while True:
        try:
            user_input = input(f"Enter source and destination floors separated by space (1-{num_floors}, 0 to stop): ")
            if user_input.strip() == "0":
                break
            source, destination = map(int, user_input.strip().split())
            if 1 <= source <= num_floors and 1 <= destination <= num_floors and source != destination:
                system.request_elevator(source, destination)
            else:
                print("Invalid input. Make sure floors are in range and not the same.")
        except ValueError:
            print("Invalid input. Please enter two floor numbers separated by space.")

if __name__ == "__main__":
    main()