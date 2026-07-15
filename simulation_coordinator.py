import traffic_lights
import traffic_lights_dynamic
import roundabout
import stop_sign
import csv
import numpy as np
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, PULP_CBC_CMD
import traceback

def optimize_traffic_method_lp(results, weights, available_space):
    model = LpProblem(name="traffic_optimization", sense=LpMaximize)
    methods = list(results.keys())
    x = {method: LpVariable(name=method.replace(" ", "_"), cat="Binary") for method in methods}

    model += lpSum(
        x[method] * (
            results[method]["Normalized Delay"] * weights["Delay"] +
            results[method]["Safety"] * weights["Safety"] +
            results[method]["Pedestrians"] * weights["Pedestrians"] +
            results[method]["Eco Impact"] * weights["Eco Impact"] +
            results[method]["Maintenance Cost"] * weights["Maintenance Cost"] +
            results[method]["Construction Cost"] * weights["Construction Cost"]
        )
        for method in methods
    ), "Total_Score"
    
    model += lpSum(x[method] for method in methods) == 1, "One_Method_Only"

    if not available_space and "Roundabout" in x:
        model += x["Roundabout"] == 0, "No_Space_For_Roundabout"
    if weights["Safety"] >= 0.4 and "STOP Sign" in x:
        model += x["STOP Sign"] == 0, "No_STOP_If_High_Safety"

    solver = PULP_CBC_CMD(msg=False)
    model.solve(solver)

    best_method = None
    for method in methods:
        if x[method].value() == 1:
            best_method = method
            break
    return best_method

def run_all_simulations(hourly_traffic, weights, available_space, runs=10):
    methods = {
        "Traffic Lights": traffic_lights.traffic_light_simulation,
        "Dynamic Traffic Lights": traffic_lights_dynamic.traffic_light_dynamic_simulation,
        "Roundabout": roundabout.roundabout_simulation,
        "STOP Sign": stop_sign.traffic_simulation
    }

    safety_scores = {
        "Traffic Lights": 6.0, "Dynamic Traffic Lights": 7.0, "Roundabout": 10.0, "STOP Sign": 2.0
    }
    pedestrian_friendly_scores = {
        "Traffic Lights": 8.0, "Dynamic Traffic Lights": 9.0, "Roundabout": 6.0, "STOP Sign": 3.0
    }
    eco_impact_scores = {
        "Traffic Lights": 5.0, "Dynamic Traffic Lights": 8.0, "Roundabout": 10.0, "STOP Sign": 4.0
    }
    maintenance_cost_scores = {
        "Traffic Lights": 4.42, "Dynamic Traffic Lights": 1.0, "Roundabout": 9.2, "STOP Sign": 10.0
    }
    construction_cost_scores = {
        "Traffic Lights": 6.1, "Dynamic Traffic Lights": 4.77, "Roundabout": 1.0, "STOP Sign": 10.0
    }

    aggregated_results = {}

    for method_name, simulation_function in methods.items():
        all_delays_runs = []
        avg_delays = []
        over20_counts = []
        print(f"\nRunning {method_name} simulation {runs} times...")
        for i in range(runs):
            try:
                sim_result = simulation_function(hourly_traffic)
                if isinstance(sim_result, tuple) and len(sim_result) == 3:
                    _, avg, delays = sim_result
                elif isinstance(sim_result, tuple) and len(sim_result) == 2:
                    avg, delays = sim_result
                else:
                    avg = sim_result
                    delays = []
                avg_delays.append(avg)
                all_delays_runs.append(delays)
                over20_counts.append(sum(1 for d in delays if d > 20))
            except Exception as e:
                print(f"Error in {method_name} run {i+1}: {e}")
                traceback.print_exc()

        all_delays_flat = [d for sublist in all_delays_runs for d in sublist]
        avg_delay = np.mean(avg_delays)
        variance_delay = np.var(avg_delays)
        avg_over20 = np.mean(over20_counts)

        aggregated_results[method_name] = {
            "Average Delay": avg_delay,
            "Delay Variance": variance_delay,
            "Over20Count": avg_over20,
            "Safety": safety_scores[method_name],
            "Pedestrians": pedestrian_friendly_scores[method_name],
            "Eco Impact": eco_impact_scores[method_name],
            "Maintenance Cost": maintenance_cost_scores[method_name],
            "Construction Cost": construction_cost_scores[method_name],
            "AllDelays": all_delays_flat,
            "AvgDelays": avg_delays,
        }

    # === Normalize Delay with Min-Max Scaling ===
    min_delay = min(res["Average Delay"] for res in aggregated_results.values())
    max_delay = max(res["Average Delay"] for res in aggregated_results.values())
    for res in aggregated_results.values():
        if max_delay == min_delay:
            res["Normalized Delay"] = 10.0
        else:
            res["Normalized Delay"] = (max_delay - res["Average Delay"]) / (max_delay - min_delay) * 10.0

    print("\n======= FINAL SCORES =======")
    for method, data in aggregated_results.items():
        score = (
            data["Normalized Delay"] * weights["Delay"] +
            data["Safety"] * weights["Safety"] +
            data["Pedestrians"] * weights["Pedestrians"] +
            data["Eco Impact"] * weights["Eco Impact"] +
            data["Maintenance Cost"] * weights["Maintenance Cost"] +
            data["Construction Cost"] * weights["Construction Cost"]
        )
        print(f"{method}: {score:.3f}")

    best_method = optimize_traffic_method_lp(aggregated_results, weights, available_space)

    print("\n======= DETAILED RESULTS =======")
    for method, data in aggregated_results.items():
        print(f"\n{method}:")
        print(f"  Average Delay: {data['Average Delay']:.2f} sec")
        print(f"  Delay Variance: {data['Delay Variance']:.4f}")
        print(f"  Average vehicles with delay >20s: {data['Over20Count']:.2f}")
        print(f"  Normalized Delay: {data['Normalized Delay']:.2f}/10")
        print(f"  Safety: {data['Safety']}/10")
        print(f"  Pedestrian Friendliness: {data['Pedestrians']}/10")
        print(f"  Eco Impact: {data['Eco Impact']}/10")
        print(f"  Maintenance Cost: {data['Maintenance Cost']}/10")
        print(f"  Construction Cost: {data['Construction Cost']}/10")
        print(f"  Total vehicles passed: {len(data['AllDelays'])}")

    print(f"\nBest method using Integer Linear Programming: {best_method}")

    print("\n======= OPTIMAL/AVERAGE GREEN TIMES =======")
    if hasattr(traffic_lights, "last_green_times") and traffic_lights.last_green_times:
        print("Traffic Lights - Optimal green time per road:")
        for road, t in traffic_lights.last_green_times.items():
            print(f"   {road}: {t} seconds")
    if hasattr(traffic_lights_dynamic, "last_avg_green_times") and traffic_lights_dynamic.last_avg_green_times:
        print("Dynamic Traffic Lights - Average green time per road:")
        for road, avg in traffic_lights_dynamic.last_avg_green_times.items():
            print(f"   {road}: {avg:.1f} seconds")

    import os
    os.makedirs("detailed", exist_ok=True)
    with open("simulation_results.csv", "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Method", "Average Delay", "Delay Variance", "Avg Over 20s", "Normalized Delay"
        ])
        for method, data in aggregated_results.items():
            writer.writerow([
                method,
                f"{data['Average Delay']:.4f}",
                f"{data['Delay Variance']:.4f}",
                f"{data['Over20Count']:.2f}",
                f"{data['Normalized Delay']:.2f}"
            ])

    with open("detailed/simulation_runs_delays.csv", "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Method"] + [f"Run_{i+1}" for i in range(runs)] + ["Average"])
        for method_name, data in aggregated_results.items():
            avg_delays = data.get("AvgDelays", [])
            row = [method_name] + [f"{v:.4f}" for v in avg_delays] + [f"{np.mean(avg_delays):.4f}" if avg_delays else ""]
            writer.writerow(row)

    print("\nSimulation stats saved to simulation_results.csv and detailed/simulation_runs_delays.csv")
    return aggregated_results

if __name__ == "__main__":
    hourly_traffic = {
        'South': 500,
        'East': 300,
        'North': 600,
        'West': 400
    }

    weights = {
        "Delay": 0.5,
        "Safety": 0.28,
        "Pedestrians": 0.07,
        "Eco Impact": 0.05,
        "Maintenance Cost": 0.05,
        "Construction Cost": 0.05
    }

    available_space = True
    run_all_simulations(hourly_traffic, weights, available_space, runs=10)