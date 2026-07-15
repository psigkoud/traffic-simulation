import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

# === 1. Read Data ===
if not os.path.exists('simulation_results.csv'):
    # Generate dummy data for testing purposes
    df = pd.DataFrame({
        'Method': ["Traffic Lights", "Dynamic Traffic Lights", "Roundabout", "STOP Sign"],
        'Average Delay': [15.42, 11.20, 8.15, 25.30],
        'Delay Variance': [4.12, 2.10, 1.15, 12.50]
    })
else:
    df = pd.read_csv('simulation_results.csv')

method_translate = {
    "Traffic Lights": "Traffic\nLights",
    "Dynamic Traffic Lights": "Dynamic\nTraffic Lights",
    "Roundabout": "Roundabout",
    "STOP Sign": "STOP\nSign"
}
df['Method'] = df['Method'].map(lambda m: method_translate.get(m, m))

criteria = [
    "Delay", "Safety", "Pedestrians", "Eco Impact", "Maintenance", "Construction"
]

manual_scores = {
    "Traffic\nLights":         [0.0, 6.0, 8.0, 5.0, 4.42, 6.1],
    "Dynamic\nTraffic Lights": [0.0, 7.0, 9.0, 8.0, 1.00, 4.77],
    "Roundabout":              [0.0, 10.0, 6.0, 10.0, 9.20, 1.0],
    "STOP\nSign":              [0.0, 2.0, 3.0, 4.0, 10.00, 10.0]
}

weights = {
    "Delay": 0.5,
    "Safety": 0.28,
    "Pedestrians": 0.07,
    "Eco Impact": 0.05,
    "Maintenance": 0.05,
    "Construction": 0.05
}

# Normalize delay (higher score = better delay performance)
min_delay = df['Average Delay'].min()
max_delay = df['Average Delay'].max()
if max_delay == min_delay:
    df['Normalized Delay'] = 10.0
else:
    df['Normalized Delay'] = (max_delay - df['Average Delay']) / (max_delay - min_delay) * 10.0

for _, row in df.iterrows():
    if row['Method'] in manual_scores:
        manual_scores[row['Method']][0] = row['Normalized Delay']

methods = list(manual_scores.keys())
scores_matrix = np.array([manual_scores[m] for m in methods])

# === RADAR CHART ===
def plot_radar(methods, scores_matrix, criteria, save_path):
    labels = np.array(criteria)
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#222831')
    ax.set_facecolor('#222831')

    # Color palette
    palette = ['#4F8DFD', '#38D6AE', '#FEB139', '#FF6363']

    for idx, (method, values) in enumerate(zip(methods, scores_matrix)):
        values = list(values) + [values[0]]
        ax.plot(angles, values, label=method.replace('\n', ' '), color=palette[idx], linewidth=2)
        ax.fill(angles, values, color=palette[idx], alpha=0.16)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids([], labels=[])
    
    for angle, label in zip(angles[:-1], labels):
        ax.text(angle, 11.2, label, size=16, color='white', ha='center', va='center', fontweight='bold')
    
    ax.set_ylim(0, 10)
    ax.tick_params(colors='white', labelsize=13)
    for spine in ax.spines.values():
        spine.set_color('white')
    ax.grid(color='white', alpha=0.13)
    
    plt.title("MCDA Criteria Comparison per Method\n(Kapsali Camp and 20th of October Intersection)", 
              y=1.13, fontsize=18, color='white', fontweight='bold')
    
    plt.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, -0.07),
        fontsize=14,
        ncol=2,
        frameon=False,
        labelcolor='white'
    )
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig(save_path, facecolor='#222831', dpi=300, bbox_inches='tight', pad_inches=0.12)
    plt.close()

# === STACKED BAR CHART ===
def plot_stacked_bar(methods, scores_matrix, criteria, weights, save_path):
    weighted_matrix = np.zeros_like(scores_matrix)
    for i, crit in enumerate(criteria):
        weighted_matrix[:, i] = scores_matrix[:, i] * weights[crit]

    bottoms = np.zeros(len(methods))
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#222831')
    ax.set_facecolor('#222831')

    # Color palette
    palette = ['#4F8DFD', '#38D6AE', '#FEB139', '#FF6363', '#B3A0FF', '#FFB6B9']

    bar_width = 0.38
    bar_positions = np.arange(len(methods)) * 0.8

    for i in range(len(criteria)):
        values = weighted_matrix[:, i]
        bar_colors = [palette[i % len(palette)]] * len(methods)
        ax.bar(bar_positions, values, bottom=bottoms,
               color=bar_colors, edgecolor='white', label=criteria[i], width=bar_width)
        bottoms += values

    # Adjust clean labels on X-axis (remove the formatting newline if wanted, but standard is fine)
    clean_methods = [m.replace('\n', ' ') for m in methods]
    ax.set_xticks(bar_positions)
    ax.set_xticklabels(clean_methods, fontsize=16, color='white', ha='center')
    ax.set_ylabel('Total Weighted Score', fontsize=18, color='white', labelpad=13)
    ax.set_xlabel('Methods', fontsize=18, color='white', labelpad=12)
    ax.set_title("MCDA Weighted Score Decomposition\n(Kapsali Camp and 20th of October Intersection)", 
                 color='white', fontsize=20, fontweight='bold', pad=22)
    ax.tick_params(axis='y', labelsize=14, colors='white')
    for spine in ax.spines.values():
        spine.set_color('white')
    ax.grid(axis='y', alpha=0.22, color='white')

    plt.legend(
        loc='center left',
        bbox_to_anchor=(1.01, 0.5),
        fontsize=14,
        frameon=False,
        labelcolor='white'
    )
    plt.tight_layout(rect=[0, 0, 1, 1])
    plt.savefig(save_path, facecolor='#222831', dpi=300, bbox_inches='tight', pad_inches=0.14)
    plt.close()

if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    plot_radar(methods, scores_matrix, criteria, "results/comparisoncriteria.jpg")
    plot_stacked_bar(methods, scores_matrix, criteria, weights, "results/ratinganalysis.jpg")
    print("MCDA charts saved to 'results/' directory.")