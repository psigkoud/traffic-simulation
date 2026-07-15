import numpy as np
from collections import deque

START_STOP_DELAY = 2  # Startup delay if vehicle waits

last_green_times = {}

def calculate_green_times(hourly_traffic, cycle_time):
    total_traffic = sum(hourly_traffic.values())
    MIN_GREEN_TIME = cycle_time // 12
    if total_traffic == 0:
        return {road: MIN_GREEN_TIME for road in hourly_traffic}
    return {
        road: max(MIN_GREEN_TIME, int((hourly_traffic[road] / total_traffic) * cycle_time))
        for road in hourly_traffic
    }

def traffic_light_simulation(hourly_traffic, verbose=False):
    global last_green_times

    best_cycle = None
    best_delay = float('inf')
    best_delays = []

    for cycle_time in range(30, 120):  # From 30 to 120 seconds
        vehicle_id = 1
        total_time = 0
        total_cycles = 3600 // cycle_time

        roads = {road: deque() for road in hourly_traffic}
        arrival_times = {road: deque() for road in hourly_traffic}
        waiting_times = {road: [] for road in hourly_traffic}
        vehicles_passed = {road: 0 for road in hourly_traffic}

        green_times = calculate_green_times(hourly_traffic, cycle_time)

        for _ in range(total_cycles):
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

            for road in roads:
                t = 0
                while t < green_times[road]:
                    current_time = total_time + t
                    if roads[road] and arrival_times[road][0] <= current_time:
                        arrival_time = arrival_times[road].popleft()
                        roads[road].popleft()
                        if current_time == arrival_time:
                            delay = 0
                            t += 1
                        else:
                            delay = current_time - arrival_time + START_STOP_DELAY
                            t += START_STOP_DELAY
                        waiting_times[road].append(delay)
                        vehicles_passed[road] += 1
                        if verbose:
                            print(f"{road}: Vehicle, Arrival {arrival_time}, Service {current_time}, Delay {delay}s")
                    else:
                        t += 1
            total_time += cycle_time

        total_network_wait = sum(sum(waits) for waits in waiting_times.values())
        total_vehicles = sum(vehicles_passed.values())
        avg_network_wait = total_network_wait / total_vehicles if total_vehicles > 0 else 0

        if avg_network_wait < best_delay:
            best_delay = avg_network_wait
            best_cycle = cycle_time
            best_delays = []
            for waits in waiting_times.values():
                best_delays.extend(waits)

    last_green_times = calculate_green_times(hourly_traffic, best_cycle)

    return best_cycle, best_delay, best_delays

if __name__ == "__main__":
    hourly_traffic = {'North': 100, 'South': 101, 'East': 99, 'West': 90}
    best_cycle, avg_delay, all_delays = traffic_light_simulation(hourly_traffic, verbose=True)
    print("Best cycle:", best_cycle)
    print("Average delay:", avg_delay)
    print("Vehicles with delay > 20s:", sum(1 for d in all_delays if d > 20))