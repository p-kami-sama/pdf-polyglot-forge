import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

IEEE_WIDTH = 3.4
IEEE_HEIGHT = 2.5

plt.rcParams.update({
    'figure.figsize': (IEEE_WIDTH, IEEE_HEIGHT),
    'figure.constrained_layout.use': True,
    'font.size': 9,
    'axes.labelsize': 9,
    'xtick.labelsize': 7.5,
    'ytick.labelsize': 9,
    'font.family': 'serif',

    'lines.linewidth': 0.6,
    'axes.linewidth': 0.5,
    'grid.linewidth': 0.3,
    'axes.axisbelow': True
})

data_file_name = "NEW_PDF_tests.csv"
output_graph_file_name = "graphics/5_google_detection_by_polyglot_type.pdf"

# 1. Load and clear the data
df = pd.read_csv(data_file_name)
df = df.dropna(how="all").copy()
df.columns = [c.strip() for c in df.columns]


def parse_google_status(val):
    val = str(val).lower().strip()
    if "infected" in val:
        return 100.0
    # We assume that 'clean', 'warning' or anything else is 0 detection
    return 0.0


df["Google_Pct"] = df["Google"].apply(parse_google_status)

# Calculate the average grouped by type
grouped = df.groupby("polyglot type")["Google_Pct"].mean()

# Reorder to make logical sense
order = ["clear", "start", "middle", "end"]
grouped = grouped.reindex(order)


fig, ax = plt.subplots()

# Draw bars
my_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", ]

# Pasamos la lista 'my_colors' al parámetro 'color'
bars = ax.bar(grouped.index, grouped.values, color=my_colors, edgecolor='black', width=0.6, linewidth=0.5)

# Axis Configuration
ax.set_ylabel("Detection Rate (%)")
ax.set_xlabel("Polyglot Position")
ax.set_ylim(0, 115)

# Grid
ax.yaxis.set_major_locator(mticker.MultipleLocator(20))
ax.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.7)

# Add the values ​​above the bars
for bar in bars:
    height = bar.get_height()
    y_pos = height + 2 if height > 0 else 2 
    
    ax.text(bar.get_x() + bar.get_width()/2., y_pos,
            f'{height:.1f}%',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

# Save the graph
output_dir = os.path.dirname(output_graph_file_name)
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir)

plt.savefig(output_graph_file_name)
print(f"Graph saved as: {output_graph_file_name}")