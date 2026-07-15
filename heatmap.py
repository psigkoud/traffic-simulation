import matplotlib.pyplot as plt
import numpy as np
import os

# Method and criterion names (without delay)
methods = [
    "Traffic Lights",
    "Dynamic Traffic Lights",
    "Roundabout",
    "STOP Sign"
]
criteria = [
    "Safety", "Pedestrians", "Eco-Friendliness", "Maintenance", "Construction"
]

# Scores (WITHOUT Delay)
scores = np.array([
    [6.0, 8.0, 5.0, 4.42, 6.1],   # Traffic Lights
    [7.0, 9.0, 8.0, 1.00, 4.77],   # Dynamic Traffic Lights
    [10.0, 6.0, 10.0, 9.20, 1.0],  # Roundabout
    [2.0, 3.0, 4.0, 10.00, 10.0]   # STOP Sign
])

fig, ax = plt.subplots(figsize=(10, 5))

# Heatmap with "viridis" colormap
im = ax.imshow(scores, cmap="viridis", aspect="auto", vmin=0, vmax=10)

# Labels
ax.set_xticks(np.arange(len(criteria)))
ax.set_yticks(np.arange(len(methods)))
ax.set_xticklabels(criteria, fontsize=15, color='white', rotation=25, ha='right', fontweight='bold')
ax.set_yticklabels(methods, fontsize=15, color='white', fontweight='bold')

# Display values inside cells
for i in range(len(methods)):
    for j in range(len(criteria)):
        value = scores[i, j]
        text_color = "white" if value < 6 else "black"
        ax.text(j, i, f"{value:.1f}", ha="center", va="center",
                fontsize=14, color=text_color, fontweight="bold")

# Styling and customization
ax.set_title("Multi-Criteria Evaluation Heatmap (No Delay)",
             color="white", fontsize=19, pad=22, fontweight='bold', loc='center')
fig.patch.set_facecolor('black')
ax.set_facecolor('black')
cbar = fig.colorbar(im, ax=ax, orientation="vertical", fraction=0.03, pad=0.04)
cbar.ax.yaxis.set_tick_params(color='white', labelsize=13)
plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white', fontweight='bold')
ax.tick_params(axis='x', labelsize=14, colors='white')
ax.tick_params(axis='y', labelsize=14, colors='white')
for spine in ax.spines.values():
    spine.set_color('white')

plt.tight_layout()
os.makedirs('results', exist_ok=True)
plt.savefig("results/heatmap_no_delay.png", dpi=300, facecolor='black')
plt.show()