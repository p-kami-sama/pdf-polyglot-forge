import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

IEEE_WIDTH = 3.4
IEEE_HEIGHT = 3.2

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
output_graph_file_name = "graphics/3_detection_by_platform.pdf"
binarize_values = False     # Switch to True to binarize detections

# 1. Load and clear the data
df_raw = pd.read_csv(data_file_name)
df = df_raw.dropna(how="all").copy()
df.columns = [c.strip() for c in df.columns]

# 2. Configure the chart
def ratio_to_percent(value):
    if isinstance(value, str) and "/" in value:
        detected, total = value.split("/")
        if binarize_values:
            return 100.0 if int(detected) > 0 else 0.0
        else:
            return (int(detected) / int(total)) * 100
    elif value == "infected":
        return 100.0
    elif value in ("clean", "warning"):
        return 0.0
    else:
        print(f"VALOR INESPERADO: {value}")
        return None

platform_columns = [
    "VirusTotal",
    "Hybrid Analysis",
    "MetaDefender Cloud",
    "Jotti’s Malware Scan",
]

for col in platform_columns:
    df.loc[:, col] = df[col].apply(ratio_to_percent)

# 3. Calculate the average detection rate per platform
platform_means = df[platform_columns].mean()


# 4. Create the bar chart
my_colors = ["#c6dbef", "#9ecae1", "#6baed6", "#3182bd"]
ax = platform_means.plot(kind="bar", color=my_colors, edgecolor="black", linewidth=0.5)

plt.grid(axis='y', linestyle='--', linewidth=0.3, which='both')
plt.gca().set_axisbelow(True)

ax.yaxis.set_major_locator(mticker.MultipleLocator(10))
ax.yaxis.set_minor_locator(mticker.MultipleLocator(5))

plt.ylabel("Detection Rate (%)")
plt.xlabel("Analysis Platform")

plt.xticks(rotation=25, ha="right")


# 5. Save the graph
output_dir = os.path.dirname(output_graph_file_name)
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir)

plt.savefig(output_graph_file_name)
plt.close()

print(f"Graph saved as: {output_graph_file_name}")
