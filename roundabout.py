import random
import numpy as np
from collections import deque

# Roundabout Simulation Constants
CYCLE_TIME = 60
TOTAL_CYCLES = 3600 // CYCLE_TIME
VEHICLE_PASS_TIME = 2
CHECK_TIME = 2
ROUNDABOUT_CAPACITY = 4

def roundabout_simulation(hourly_traffic, verbose=False):
    vehicle_id = 1
    total_time = 0

    roads = {road: deque() for road in hourly_traffic}
    arrival_times = {road: deque() for road in hourly_traffic}
    waiting_times = {road: [] for road in hourly_traffic}
    vehicles_passed = {road: 0 for road in hourly_traffic}
    total_waiting_time = {road: 0 for road in hourly_traffic}

    roundabout = deque()
    roundabout_exit_time = {}

    for cycle in range(TOTAL_CYCLES):
        if verbose:
            print(f"\n======= CYCLE {cycle + 1} =======")

        for road in hourly_traffic:
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

        for t in range(CYCLE_TIME):
            current_time = total_time + t
            for road in roads:
                while roads[road] and arrival_times[road][0] <= current_time and len(roundabout) < ROUNDABOUT_CAPACITY:
                    vehicle = roads[road].popleft()
                    arrival_time = arrival_times[road].popleft()
                    entry_time = current_time
                    queue_wait = entry_time - arrival_time
                    exit_steps = random.randint(1, 3)
                    extra_time_in_roundabout = exit_steps * VEHICLE_PASS_TIME
                    exit_time = entry_time + extra_time_in_roundabout
                    roundabout.append(vehicle)
                    roundabout_exit_time[vehicle] = exit_time
                    total_wait_time = queue_wait + CHECK_TIME + extra_time_in_roundabout  # Does NOT include transit time
                    total_waiting_time[road] += total_wait_time
                    waiting_times[road].append(total_wait_time)
                    if verbose:
                        print(
                            f"{vehicle} ({road}) | Arrival: {arrival_time}s | Entry: {entry_time}s | "
                            f"Queue Wait: {queue_wait}s | CHECK: {CHECK_TIME}s | "
                            f"Roundabout Duration: {extra_time_in_roundabout}s | "
                            f"Delay (excl. transit): {total_wait_time}s"
                        )

            vehicles_to_remove = []
            for vehicle in list(roundabout):
                if current_time >= roundabout_exit_time[vehicle]:
                    vehicles_to_remove.append(vehicle)

            for vehicle in vehicles_to_remove:
                roundabout.remove(vehicle)
                exit_road = random.choice(list(roads.keys()))
                vehicles_passed[exit_road] += 1
                del roundabout_exit_time[vehicle]
                if verbose:
                    print(f"{vehicle} exits the roundabout via {exit_road}")

        total_time += CYCLE_TIME

    total_network_wait = sum(total_waiting_time.values())
    total_vehicles = sum(vehicles_passed.values())
    avg_network_wait = total_network_wait / total_vehicles if total_vehicles > 0 else 0

    all_delays = []
    for road_delays in waiting_times.values():
        all_delays.extend(road_delays)

    if verbose:
        print("\n======= FINAL STATISTICS =======")
        for road in roads:
            avg_wait = total_waiting_time[road] / vehicles_passed[road] if vehicles_passed[road] else 0
            print(f"{road}: Average Delay: {avg_wait:.2f}s | Vehicles Passed: {vehicles_passed[road]}")
        print(f"\nTotal Network Delay: {total_network_wait:.2f}s")
        print(f"Average Delay per Vehicle: {avg_network_wait:.2f}s")

    return avg_network_wait, all_delays

# Example Usage
if __name__ == "__main__":
    hourly_traffic = {
        'North': 400,
        'South': 450,
        'East': 450,
        'West': 450
    }
    avg, delays = roundabout_simulation(hourly_traffic, verbose=True)
    print("\nAverage delay:", avg)
    print("Vehicles with delay > 20s:", sum(1 for d in delays if d > 20))