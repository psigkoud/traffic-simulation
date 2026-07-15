import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import csv
import numpy as np
import os

# --- Read Data ---
methods = []
runs_data = []
means = []

method_translate = {
    "Traffic Lights": "Traffic Lights",
    "Dynamic Traffic Lights": "Dynamic Traffic Lights",
    "Roundabout": "Roundabout",
    "STOP Sign": "STOP Sign"
}

os.makedirs("detailed", exist_ok=True)
run_file = 'detailed/simulation_runs_delays.csv'

if not os.path.exists(run_file):
    print("Creating mock runs data for plotting.")
    # Create mock detailed delays per run
    with open(run_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Method", "Run_1", "Run_2", "Run_3", "Run_4", "Run_5", "Run_6", "Run_7", "Run_8", "Run_9", "Run_10", "Average"])
        writer.writerow(["Traffic Lights", "15.1", "16.2", "14.8", "15.5", "16.0", "15.2", "14.9", "15.8", "16.1", "14.6", "15.42"])
        writer.writerow(["Dynamic Traffic Lights", "11.0", "11.5", "10.8", "11.2", "11.6", "11.1", "10.9", "11.4", "11.7", "10.8", "11.20"])
        writer.writerow(["Roundabout", "8.0", "8.3", "7.9", "8.2", "8.5", "8.1", "7.8", "8.4", "8.3", "8.0", "8.15"])
        writer.writerow(["STOP Sign", "24.5", "26.1", "23.8", "25.2", "26.5", "25.0", "24.2", "25.8", "26.0", "24.9", "25.30"])

with open(run_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    headers = next(reader)
    run_count = sum(1 for h in headers if h.startswith("Run_"))
    
    for row in reader:
        method_en = row[0]
        methods.append(method_translate.get(method_en, method_en))
        runs = [float(x) for x in row[1:1+run_count]]
        runs_data.append(runs)
        means.append(np.mean(runs))

# --- Load Background Image ---
bg_img_path = 'giannitsa.jpg'
if not os.path.exists(bg_img_path):
    bg_img = np.ones((100, 100, 3)) * 0.15  # Dark fallback matrix
else:
    bg_img = mpimg.imread(bg_img_path)

plt.style.use('default')
bar_width = 0.6

fig, ax = plt.subplots(figsize=(12, 7))
ymax = max(max(runs) for runs in runs_data) * 1.25
ax.imshow(bg_img, extent=[-0.5, len(methods)-0.5, 0, ymax], aspect='auto', alpha=0.5, zorder=0)

palette = ['#4F8DFD', '#38D6AE', '#FEB139', '#FF6363']
bars = ax.bar(methods, means, color=palette, width=bar_width, edgecolor='white', linewidth=1.5, zorder=2)

# Scatter plot representing 10 runs in Green
dot_color = "#00FF00"

for i, runs in enumerate(runs_data):
    ax.scatter(
        [i] * len(runs), runs,
        color=dot_color, alpha=0.7, s=100, edgecolor='black', zorder=3, label='_nolegend_'
    )
    # Average mark represented as a red line across each bar
    ax.hlines(means[i], i-bar_width/2, i+bar_width/2, colors='red', linestyles='-', lw=2.4, zorder=4)
    # Value annotation text
    ax.annotate(f'{means[i]:.2f}', xy=(i, means[i]), xytext=(0, 8), textcoords="offset points",
                ha='center', va='bottom', fontsize=13, fontweight='bold', color='white', zorder=5)

ax.set_title('Average Delay and Distribution of 10 simulation runs per Method', fontsize=20, pad=17, color='white')
ax.set_ylabel('Average Delay (seconds)', fontsize=14, color='white')
ax.set_xlabel('Methods', fontsize=14, color='white')
ax.set_facecolor('black')
fig.patch.set_facecolor('black')
ax.tick_params(axis='x', labelsize=12, colors='white', rotation=0)
ax.tick_params(axis='y', labelsize=12, colors='white')
for spine in ax.spines.values():
    spine.set_color('white')

plt.subplots_adjust(bottom=0.20)
plt.tight_layout()
plt.savefig('avg_delay_per_method_with_runs.png', dpi=300, facecolor='black')
plt.close()

print("Run analysis plot successfully created and saved.")