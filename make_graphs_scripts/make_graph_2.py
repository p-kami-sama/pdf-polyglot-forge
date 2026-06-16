import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

# Dimension configuration
IEEE_WIDTH = 3.4
IEEE_HEIGHT = 2.6  

plt.rcParams.update({
    'figure.figsize': (IEEE_WIDTH, IEEE_HEIGHT),
    'figure.constrained_layout.use': True,
    'font.size': 8.5,
    'axes.labelsize': 8.5,
    'xtick.labelsize': 7.5,
    'ytick.labelsize': 7.5,
    'legend.fontsize': 6.8,
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'lines.linewidth': 0.5,
    'axes.linewidth': 0.5,
    'grid.linewidth': 0.3,
    'axes.axisbelow': True,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})

def generate_compact_stacked_chart(data_file_name, output_graph_path):
    

    if not data_file_name.exists():
        print(f"[-] Error: {data_file_name} no encontrado.")
        return

    # 2. Load and prepare data
    df = pd.read_csv(data_file_name)
    df.columns = [c.strip() for c in df.columns]
    
    df['polyglot type'] = df['polyglot type'].fillna('unknown').str.strip().str.capitalize()
    df['obfuscated'] = df['obfuscated'].astype(str).str.strip().map({'True': 'Obfuscated', 'False': 'Clear'})
    df['vt_malicious'] = pd.to_numeric(df['vt_malicious'], errors='coerce').fillna(0).astype(int)

    # 3. Define bins and labels for VirusTotal malicious detection counts
    bins = [-1, 0, 4, 9, 14, 19, 100]
    labels = ['0', '1-4', '5-9', '10-14', '15-19', '20+']
    df['VT_Range'] = pd.cut(df['vt_malicious'], bins=bins, labels=labels)

    order_tech = ['Original', 'Stack', 'Cavity', 'Zipper']
    
    # 4. Group data by VT_Range, polyglot type, and obfuscation status
    grouped = df.groupby(['VT_Range', 'polyglot type', 'obfuscated'], observed=False).size().unstack(fill_value=0)
    
    # 5. Graph configuration
    fig, ax = plt.subplots()
    
    # Paired color palette (Light base for Clear, dark version for Obfuscated)
    color_map = {
        ('Original', 'Clear'): '#9ecae1', ('Original', 'Obfuscated'): '#084594',
        ('Stack', 'Clear'):    '#a1d99b', ('Stack', 'Obfuscated'):    '#238b45',
        ('Cavity', 'Clear'):   '#fdd0a2', ('Cavity', 'Obfuscated'):   '#d94801',
        ('Zipper', 'Clear'):   '#dabcff', ('Zipper', 'Obfuscated'):   '#6a3d9a'
    }

    # Parameters for grouped bar positions
    n_ranges = len(labels)
    n_techs = len(order_tech)
    total_width = 0.8  
    bar_width = total_width / n_techs
    
    x_indexes = np.arange(n_ranges)
    
    # Temporary lists to capture the legend handles in an orderly manner
    clear_handles = []
    obf_handles = []
    
    # Draw the bars one by one
    for j, tech in enumerate(order_tech):
        x_offsets = x_indexes - (total_width / 2) + (j * bar_width) + (bar_width / 2)
        
        clear_vals = np.array([grouped.loc[(r, tech), 'Clear'] if (r, tech) in grouped.index else 0 for r in labels])
        obf_vals = np.array([grouped.loc[(r, tech), 'Obfuscated'] if (r, tech) in grouped.index else 0 for r in labels])
        
        # 1st layer of the bar: 'Clear' samples
        b_clear = ax.bar(
            x_offsets, clear_vals, 
            width=bar_width, 
            color=color_map[(tech, 'Clear')], 
            edgecolor='black', linewidth=0.3,
            label=f"{tech} (Clear)"
        )
        
        # 2nd layer of the bar (Stacked on top): 'Obfuscated' samples
        b_obf = ax.bar(
            x_offsets, obf_vals, 
            bottom=clear_vals,  
            width=bar_width, 
            color=color_map[(tech, 'Obfuscated')], 
            edgecolor='black', linewidth=0.3,
            label=f"{tech} (+Obf.)"
        )
        
        # We save the first rectangle of each series to create the personalized legend
        clear_handles.append((b_clear[0], f"{tech} (Clear)"))
        obf_handles.append((b_obf[0], f"{tech} (+Obf.)"))

    # 6. Explicit reordering of the legend into two semantic columns
    # We merge the two lists: first, all those in the Clear column, and then all those in Obfuscated.
    ordered_elements = clear_handles + obf_handles
    handles_final = [item[0] for item in ordered_elements]
    labels_final = [item[1] for item in ordered_elements]

    ax.set_xlabel("VirusTotal Detection Range")
    ax.set_ylabel("Number of Samples")
    
    ax.set_xticks(x_indexes)
    ax.set_xticklabels(labels)
    
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    
    # Draw the legend with two columns
    ax.legend(
        handles=handles_final,
        labels=labels_final,
        loc="upper right",
        ncol=2,
        columnspacing=0.5,
        handletextpad=0.2,
        borderpad=0.2,
        framealpha=0.9,
        edgecolor='black',
        fontsize=7.4
    )
    
    # Adjust Y-axis limits with a small margin for the legend
    ax.set_ylim(0, ax.get_ylim()[1] * 1.15)

    plt.savefig(output_graph_path, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"[+] Success: Chart saved in {output_graph_path}")

if __name__ == '__main__':
    # 1. Path configuration
    script_dir = Path(__file__).resolve().parent
    data_file_name = script_dir.parent / "results.csv"
    output_graph_path = script_dir.parent / "graphs" / "2_grouped_chart_virus_total.pdf"
    output_graph_path.parent.mkdir(parents=True, exist_ok=True)
    generate_compact_stacked_chart(data_file_name, output_graph_path)
    