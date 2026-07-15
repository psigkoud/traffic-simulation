import numpy as np
from collections import deque

START_STOP_DELAY = 2  # Startup delay if vehicle waits

# This variable will be updated after each simulation run
last_avg_green_times = {}

def calculate_dynamic_green_times(roads, hourly_traffic, cycle_time, total_time):
    total_future_cars = {}
    for road in roads:
        avg_per_sec = hourly_traffic[road] / 3600
        expected_next = avg_per_sec * cycle_time
        total_future_cars[road] = len(roads[road]) + expected_next
    total_cars = sum(total_future_cars.values())
    MIN_GREEN_TIME = cycle_time // 12
    if total_cars == 0:
        return {road: MIN_GREEN_TIME for road in roads}
    return {road: max(MIN_GREEN_TIME, int((total_future_cars[road] / total_cars) * cycle_time))
            for road in roads}

def traffic_light_dynamic_simulation(hourly_traffic, verbose=False):
    global last_avg_green_times

    best_cycle = None
    best_delay = float('inf')
    all_results = {}

    best_green_history = None  # Will store green history for the optimal cycle
    best_delays = []          # Will store all delays for the optimal cycle

    for cycle_time in range(30, 120):  # From 30 to 120 seconds
        vehicle_id = 1
        total_time = 0
        total_cycles = 3600 // cycle_time  # Always 1 hour simulation

        roads = {road: deque() for road in hourly_traffic}
        arrival_times = {road: deque() for road in roads}
        waiting_times = {road: [] for road in roads}
        vehicles_passed = {road: 0 for road in roads}

        green_history = {road: [] for road in roads}

        for cycle in range(total_cycles):
            for road in roads:
                lam = hourly_traffic[road] / 3600  # Vehicles per second
                t = 0
                while t < cycle_time:
                    interarrival = np.random.exponential(1 / lam) if lam > 0 else cycle_time
                    t += interarrival
                    if t >= cycle_time:
                        break
                    arrival = total_time + int(t)
                    roads[road].append(f"Car-{vehicle_id}")
                    arrival_times[road].append(arrival)
                    vehicle_id += 1

            green_times = calculate_dynamic_green_times(roads, hourly_traffic, cycle_time, total_time)
            for road in roads:
                green_history[road].append(green_times[road])

            for road in roads:
                t = 0
                while t < green_times[road]:
                    if roads[road] and arrival_times[road][0] <= total_time + t:
                        arrival_time = arrival_times[road].popleft()
                        roads[road].popleft()
                        if (total_time + t) == arrival_time:
                            delay = 0
                            t += 1
                        else:
                            delay = (total_time + t) - arrival_time + START_STOP_DELAY
                            t += START_STOP_DELAY
                        waiting_times[road].append(delay)
                        vehicles_passed[road] += 1
                        if verbose:
                            print(f"{road}: Vehicle, Arrival {arrival_time}, Service {total_time + t}, Delay {delay}s")
                    else:
                        t += 1
            total_time += cycle_time

        total_network_wait = sum(sum(waiting_times[road]) for road in roads)
        total_vehicles = sum(vehicles_passed.values())
        avg_network_wait = total_network_wait / total_vehicles if total_vehicles else 0

        all_results[cycle_time] = avg_network_wait

        if avg_network_wait < best_delay:
            best_delay = avg_network_wait
            best_cycle = cycle_time
            best_green_history = {road: list(green_history[road]) for road in green_history}
            best_delays = []
            for waits in waiting_times.values():
                best_delays.extend(waits)

    if best_green_history:
        last_avg_green_times = {
            road: sum(best_green_history[road]) / len(best_green_history[road])
            for road in best_green_history
        }
    else:
        last_avg_green_times = {}

    return best_cycle, best_delay, best_delays

# Example usage
if __name__ == "__main__":
    hourly_traffic = {
        'North': 100,
        'South': 101,
        'East': 99,
        'West': 90
    }
    best_cycle, avg_delay, all_delays = traffic_light_dynamic_simulation(hourly_traffic, verbose=True)
    print("Best cycle:", best_cycle)
    print("Average delay:", avg_delay)
    print("Vehicles with delay > 20s:", sum(1 for d in all_delays if d > 20))