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
output_graph_file_name = "graphs/4_detection_dotplot_malware.pdf"

# 1. Load and clear the data
df = pd.read_csv(data_file_name)
df = df.dropna(how="all").copy()
df.columns = [c.strip() for c in df.columns]

def parse_fraction(val):
    if isinstance(val, str) and '/' in val:
        num, den = val.split('/')
        return (float(num) / float(den)) * 100 if float(den) > 0 else 0
    if val == "infected": return 100.0
    return 0.0

platform_cols = ["VirusTotal", "Hybrid Analysis", "MetaDefender Cloud", "Jotti’s Malware Scan"]
for col in platform_cols:
    df[col] = df[col].apply(parse_fraction)

df["Avg_Detection"] = df[platform_cols].mean(axis=1)

# Cleaning up names so they look nice on the X-axis
def clean_name(row):
    raw_name = str(row['name'])
    # We remove extensions
    name = raw_name.replace('.pdf', '').replace('.py', '').replace('.rb', '').replace('.sh', '')
    # We remove positional suffixes
    name = name.replace('_start', '').replace('_middle', '').replace('_end', '')
    # We replace underscores with spaces
    name = name.replace('_', ' ')
    return name

df['Family_Clean'] = df.apply(clean_name, axis=1)

# Sort by average detection of the original (clear) from highest to lowest
df_clear = df[df['polyglot type'] == 'clear'][['Family_Clean', 'Avg_Detection']].set_index('Family_Clean')
malware_order = df_clear.sort_values(by='Avg_Detection', ascending=False).index.tolist()

# 2. Configure the chart
fig, ax = plt.subplots()

colors = {
    'clear': '#1f77b4',
    'start': '#ff7f0e',
    'middle': '#2ca02c',
    'end': '#d62728',
}
markers = {
    'clear': 'o', 
    'start': '^', 
    'middle': 's',
    'end': 'D'    
}
labels_map = {
    'clear': 'Original (Clear)',
    'start': 'Start Polyglot',
    'middle': 'Middle Polyglot',
    'end': 'End Polyglot'
}

# 3. Plot the dots (Dot Plot)
# We iterate through each type of polyglot to draw them as separate series
for p_type in ['clear', 'start', 'middle', 'end']:
    subset = df[df['polyglot type'] == p_type]
    
    # Ensure correct order on the X-axis
    subset = subset.set_index('Family_Clean').reindex(malware_order).reset_index()
    
    x_positions = range(len(subset))
    y_values = subset['Avg_Detection']
    
    ax.scatter(x_positions, y_values, 
               color=colors[p_type], 
               marker=markers[p_type], 
               label=labels_map[p_type],
               s=50,
               alpha=0.9, 
               edgecolor='black', 
               linewidth=0.5,
               zorder=3) 


# 4. Fine-tune the graph
ax.yaxis.set_major_locator(mticker.MultipleLocator(10))
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.grid(axis='x', linestyle=':', alpha=0.3)
ax.set_axisbelow(True)

plt.ylim(0, 75) 
plt.ylabel("Average Detection Rate (%)")
plt.xlabel("Malware Family")


plt.xticks(
    ticks=range(len(malware_order)), 
    labels=malware_order, 
    rotation=25, 
    ha="right",
    rotation_mode="anchor"
)

plt.legend(
    loc="upper right",
    bbox_to_anchor=(1, 1),
    frameon=True,
    fontsize=8,
    markerscale=1.2,
    edgecolor='black',
    fancybox=False,
    framealpha=1
)

# 6. Save the graph
output_dir = os.path.dirname(output_graph_file_name)
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir)

plt.savefig(output_graph_file_name)
print(f"Graph saved as: {output_graph_file_name}")