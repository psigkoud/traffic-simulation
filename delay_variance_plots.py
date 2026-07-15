import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import csv
import numpy as np
import os

# --- Read Simulation Data ---
methods = []
avg_delays = []
variances = []
over20s = []

# Map CSV/Code names to clean plot labels
method_translate = {
    "Traffic Lights": "Traffic Lights",
    "Dynamic Traffic Lights": "Dynamic Traffic Lights",
    "Roundabout": "Roundabout",
    "STOP Sign": "STOP Sign"
}

if not os.path.exists('simulation_results.csv'):
    # Generate dummy data for plotting demonstration if file doesn't exist yet
    print("No simulation_results.csv found. Creating mock data for plotting.")
    with open('simulation_results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Method", "Average Delay", "Delay Variance", "Avg Over 20s", "Normalized Delay"])
        writer.writerow(["Traffic Lights", "15.42", "4.12", "12.0", "6.5"])
        writer.writerow(["Dynamic Traffic Lights", "11.20", "2.10", "5.0", "8.5"])
        writer.writerow(["Roundabout", "8.15", "1.15", "2.0", "10.0"])
        writer.writerow(["STOP Sign", "25.30", "12.50", "42.0", "1.0"])

with open('simulation_results.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        m = method_translate.get(row['Method'], row['Method'])
        methods.append(m)
        avg_delays.append(float(row['Average Delay']))
        variances.append(float(row['Delay Variance']))
        if 'Avg Over 20s' in row:
            over20s.append(float(row['Avg Over 20s']))

# --- Load Background Image ---
bg_img_path = 'images/image1.jpg'
if not os.path.exists(bg_img_path):
    # Fallback to white/black matrix if image missing
    bg_img = np.ones((100, 100, 3)) * 0.15  # Dark gray fallback
else:
    bg_img = mpimg.imread(bg_img_path)

plt.style.use('default')
bar_width = 0.6
palette = ['#4F8DFD', '#38D6AE', '#FEB139', '#FF6363']
os.makedirs('results', exist_ok=True)

# 1. Average Delay Chart
fig, ax = plt.subplots(figsize=(12, 7))
ymax = max(avg_delays) * 1.25
ax.imshow(bg_img, extent=[-0.5, len(methods)-0.5, 0, ymax], aspect='auto', alpha=0.5, zorder=0)

bars = ax.bar(methods, avg_delays, color=palette, width=bar_width, edgecolor='white', linewidth=1.5, zorder=2)

for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 8), textcoords="offset points",
                ha='center', va='bottom',
                fontsize=13, fontweight='bold', color='white', zorder=3)

ax.set_title('Average Delay per Control Method', fontsize=20, pad=17, color='white')
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
plt.savefig('results/avg_delay_per_method_with_bg.png', dpi=300, facecolor='black')
plt.close()

# 2. Delay Variance Chart
fig, ax = plt.subplots(figsize=(12, 7))
ymax_var = max(variances) * 1.25
ax.imshow(bg_img, extent=[-0.5, len(methods)-0.5, 0, ymax_var], aspect='auto', alpha=0.5, zorder=0)
bars2 = ax.bar(methods, variances, color=palette, width=bar_width, edgecolor='white', linewidth=1.5, zorder=2)

for bar in bars2:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 8), textcoords="offset points",
                ha='center', va='bottom',
                fontsize=13, fontweight='bold', color='white', zorder=3)

ax.set_title('Delay Variance per Control Method', fontsize=20, pad=17, color='white')
ax.set_ylabel('Variance', fontsize=14, color='white')
ax.set_xlabel('Methods', fontsize=14, color='white')
ax.set_facecolor('black')
fig.patch.set_facecolor('black')
ax.tick_params(axis='x', labelsize=12, colors='white', rotation=0)
ax.tick_params(axis='y', labelsize=12, colors='white')
for spine in ax.spines.values():
    spine.set_color('white')

plt.subplots_adjust(bottom=0.20)
plt.tight_layout()
plt.savefig('results/variance_per_method_with_bg.png', dpi=300, facecolor='black')
plt.close()

# 3. Average Vehicles with Delay >20s Chart
if over20s:
    fig, ax = plt.subplots(figsize=(12, 7))
    ymax_o20 = max(over20s) * 1.25
    ax.imshow(bg_img, extent=[-0.5, len(methods)-0.5, 0, ymax_o20], aspect='auto', alpha=0.5, zorder=0)
    bars3 = ax.bar(methods, over20s, color=palette, width=bar_width, edgecolor='white', linewidth=1.5, zorder=2)
    
    for bar in bars3:
        height = bar.get_height()
        ax.annotate(f'{height:.0f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 8), textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=13, fontweight='bold', color='white', zorder=3)

    ax.set_title('Average Number of Vehicles with Delay > 20s', fontsize=20, pad=17, color='white')
    ax.set_ylabel('Vehicle Count', fontsize=14, color='white')
    ax.set_xlabel('Methods', fontsize=14, color='white')
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')
    ax.tick_params(axis='x', labelsize=12, colors='white', rotation=0)
    ax.tick_params(axis='y', labelsize=12, colors='white')
    for spine in ax.spines.values():
        spine.set_color('white')

    plt.subplots_adjust(bottom=0.20)
    plt.tight_layout()
    plt.savefig('results/over20_per_method_with_bg.png', dpi=300, facecolor='black')
    plt.close()

print("Charts successfully saved to the 'results' directory.")