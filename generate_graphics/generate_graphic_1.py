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
    'font.family': 'Times New Roman',
    
    'lines.linewidth': 0.6,
    'axes.linewidth': 0.5,
    'grid.linewidth': 0.3,
    'axes.axisbelow': True
})

data_file_name = "results.csv"
output_graph_file_name = "graphics/1_detection_by_technique.pdf"

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

# 3. Prepare the bar chart
df["polyglot type"] = pd.Categorical(df["polyglot type"], categories=["clear", "start", "middle", "end"], ordered=True)
grouped = df.groupby("polyglot type", observed=True)[platform_columns].mean()

my_colors = ["#c6dbef", "#9ecae1", "#6baed6", "#3182bd"]

ax = grouped.plot(
    kind="bar", 
    width=0.7, 
    color=my_colors, 
    edgecolor="black", 
    linewidth=0.5
)

# 4. Add media lines and labels

# Calculate the overall average per technique (average of the 4 platforms)
global_means = grouped.mean(axis=1)
for i, (technique, mean_val) in enumerate(global_means.items()):
    # X coordinates for the line (covering the width of the bar group)
    x_min = i - 0.35
    x_max = i + 0.35
    
    ax.hlines(y=mean_val, xmin=x_min, xmax=x_max, 
              colors='black', 
              linewidth=0.8, 
              linestyles='--')
    
    # Text above the line
    ax.text(x=i, y=mean_val + 2, s=f"{mean_val:.1f}%", 
            color='black', ha='center', va='bottom', 
            fontweight='bold', 
            fontsize=8
    )


# 5. Fine-tune the graph
ax.yaxis.set_major_locator(mticker.MultipleLocator(10))


plt.grid(axis='y', linestyle='--', linewidth=0.3, which='both')
plt.gca().set_axisbelow(True)

plt.legend(
    loc="upper right",
    bbox_to_anchor=(1, 1),
    borderaxespad=0.0,
    edgecolor='black',
    framealpha=1,
    fontsize=7.5,
    fancybox=False
).get_frame().set_linewidth(0.5)

plt.ylabel("Detection Rate (%)")
plt.xlabel("Polyglot Construction Technique")
plt.xticks(rotation=0)

# 6. Save the graph
output_dir = os.path.dirname(output_graph_file_name)
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir)

plt.savefig(output_graph_file_name, )
plt.close()
print(f"Graph saved as: {output_graph_file_name}")