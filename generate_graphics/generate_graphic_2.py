import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

IEEE_WIDTH = 3.4
IEEE_HEIGHT = 2.8

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
output_graph_file_name = "graphics/2_boxplot_detection_by_technique.pdf"

# 1. Load and clear the data
df_raw = pd.read_csv(data_file_name)
df = df_raw.dropna(how="all").copy()
df.columns = [c.strip() for c in df.columns]

# 2. Function to convert values
def ratio_to_percent(value):
    if isinstance(value, str) and "/" in value:
        detected, total = value.split("/")
        return (int(detected) / int(total)) * 100
    elif value == "infected": return 100.0
    elif value in ("clean", "warning"): return 0.0
    else: return None

platform_columns = ["VirusTotal", "Hybrid Analysis", "MetaDefender Cloud", "Jotti’s Malware Scan"]

for col in platform_columns:
    df.loc[:, col] = df[col].apply(ratio_to_percent)

# 3. Prepare data for boxplot
desired_order = ["clear", "start", "middle", "end"]
boxplot_data = []

for technique in desired_order:
    subset = df[df["polyglot type"] == technique]
    combined = pd.concat([subset[col] for col in platform_columns])
    boxplot_data.append(combined)

# 4. Create the boxplot
bp = plt.boxplot(
    boxplot_data,
    labels=desired_order,
    patch_artist=True,
    widths=0.6,    
)

colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", ]

for patch, color in zip(bp["boxes"], colors):
    patch.set_facecolor(color)
    patch.set_edgecolor("black")
    patch.set_linewidth(0.5)

for whisker in bp['whiskers']:
    whisker.set_linewidth(0.5)

for cap in bp['caps']:
    cap.set_linewidth(0.5)
    
for median in bp['medians']:
    median.set_color('black')
    median.set_linewidth(0.8)

# 5. Axis and grid configuration
plt.grid(axis='y', linestyle='--', linewidth=0.3, which='both')
plt.gca().set_axisbelow(True)

plt.ylabel("Detection Rate (%)")
plt.xlabel("Polyglot Construction Technique")

plt.gca().yaxis.set_major_locator(mticker.MultipleLocator(20))
plt.gca().yaxis.set_minor_locator(mticker.MultipleLocator(10))

# 6. Save the graph
output_dir = os.path.dirname(output_graph_file_name)
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir)
plt.savefig(output_graph_file_name)
plt.close()

print(f"Graph saved as: {output_graph_file_name}")