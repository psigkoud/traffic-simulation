import numpy as np
from collections import deque

CYCLE_TIME = 60
TOTAL_CYCLES = 3600 // CYCLE_TIME
CROSS_TIME = 3
START_STOP_CHECK_DELAY = 5

def determine_priority(hourly_traffic):
    ns = hourly_traffic['North'] + hourly_traffic['South']
    ew = hourly_traffic['East'] + hourly_traffic['West']
    return ('North', 'South') if ns >= ew else ('East', 'West')

def traffic_simulation(hourly_traffic, verbose=False):
    vehicle_id = 1
    total_time = 0

    roads = {'North': deque(), 'South': deque(), 'East': deque(), 'West': deque()}
    arrival_times = {road: deque() for road in roads}
    waiting_times = {road: [] for road in roads}
    vehicles_passed = {road: 0 for road in roads}

    priority_roads = determine_priority(hourly_traffic)
    stop_roads = [r for r in roads if r not in priority_roads]

    for cycle in range(TOTAL_CYCLES):
        for road in roads:
            lam = hourly_traffic[road] / 3600  # lambda in vehicles per second
            t = 0
            while t < CYCLE_TIME:
                interarrival = np.random.exponential(1 / lam) if lam > 0 else CYCLE_TIME
                t += interarrival
                if t >= CYCLE_TIME:
                    break
                arrival = total_time + int(t)
                roads[road].append(f"Car-{vehicle_id}")
                arrival_times[road].append(arrival)
                vehicle_id += 1

        crossing_until = 0
        t = 0
        while t < CYCLE_TIME:
            crossing_done = False
            for road in priority_roads:
                if roads[road] and t >= crossing_until:
                    if arrival_times[road][0] > t + total_time:
                        continue
                    car = roads[road].popleft()
                    atime = arrival_times[road].popleft()
                    delay = (t + total_time) - atime
                    waiting_times[road].append(delay)
                    vehicles_passed[road] += 1
                    crossing_until = t + CROSS_TIME
                    crossing_done = True
                    if verbose:
                        print(f"{car} from {road} (PRIORITY) | Arrival: {atime}s | Crossing: {t+total_time}s | Delay: {delay}s")
                    break
            if crossing_done:
                t += 1
                continue
            for road in stop_roads:
                if roads[road] and t >= crossing_until:
                    if arrival_times[road][0] > t + total_time:
                        continue
                    car = roads[road].popleft()
                    atime = arrival_times[road].popleft()
                    start_wait = (t + total_time) - atime
                    delay = start_wait + START_STOP_CHECK_DELAY
                    waiting_times[road].append(delay)
                    vehicles_passed[road] += 1
                    crossing_until = t + CROSS_TIME
                    if verbose:
                        print(f"{car} from {road} (STOP) | Arrival: {atime}s | Crossing: {t+total_time}s | Delay: {delay}s (with STOP)")
                    break
            t += 1

        total_time += CYCLE_TIME

    total_network_wait = sum(sum(waiting_times[road]) for road in roads)
    total_vehicles = sum(vehicles_passed.values())
    avg_network_wait = total_network_wait / total_vehicles if total_vehicles > 0 else 0

    all_delays = []
    for waits in waiting_times.values():
        all_delays.extend(waits)

    if verbose:
        print("\n======= FINAL STATISTICS =======")
        for road in roads:
            total_wait = sum(waiting_times[road])
            avg_wait = total_wait / len(waiting_times[road]) if waiting_times[road] else 0
            print(f"{road}: Average Delay = {avg_wait:.2f}s | Vehicles Passed: {vehicles_passed[road]}")
        print(f"Total Network Delay: {total_network_wait:.2f}s")
        print(f"Average Delay per Vehicle: {avg_network_wait:.2f}s")

    return avg_network_wait, all_delays

# Example usage
if __name__ == "__main__":
    hourly_traffic = {
        'North': 100,
        'South': 101,
        'East': 99,
        'West': 90
    }
    avg, delays = traffic_simulation(hourly_traffic, verbose=True)
    print("Average delay:", avg)
    print("Vehicles with delay > 20s:", sum(1 for d in delays if d > 20))