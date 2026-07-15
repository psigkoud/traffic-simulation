# Traffic Intersection Control Simulation & MCDA

This project is a comprehensive Python-based simulation and Multi-Criteria Decision Analysis (MCDA) tool for evaluating different traffic control methods at an intersection. 

The simulation compares four distinct traffic management approaches to determine the optimal solution based on various weighted criteria, such as average delay, safety, and eco-friendliness.

## 🚦 Simulated Methods
1. **Traffic Lights** (Fixed cycle timing)
2. **Dynamic Traffic Lights** (Adaptive timing based on real-time traffic volume)
3. **Roundabout** (Continuous flow with priority rules)
4. **STOP Sign** (Standard priority and stop-and-go rules)

## 📊 Multi-Criteria Decision Analysis (MCDA)
The project doesn't just look at vehicle delays. It evaluates the optimal method using Integer Linear Programming (via `PuLP`) based on a weighted scoring system of the following criteria:
* **Delay** (Normalized based on simulation results)
* **Safety** * **Pedestrian Friendliness**
* **Eco Impact**
* **Maintenance Cost**
* **Construction Cost**

## 🛠️ Features
* **Stochastic Traffic Generation:** Uses Poisson/Exponential distributions for realistic vehicle arrival times.
* **LP Optimization:** Recommends the absolute best method using Integer Linear Programming.
* **Data Visualization:** Generates professional Radar charts, Stacked Bar charts, Heatmaps, and Scatter plots for run analysis using `matplotlib`.
* **CSV Export:** Automatically exports detailed simulation runs and aggregated results for further statistical analysis.

## 💻 Installation & Requirements
Ensure you have Python 3.8+ installed. You can install the required dependencies using:

```bash
pip install numpy pandas matplotlib pulp