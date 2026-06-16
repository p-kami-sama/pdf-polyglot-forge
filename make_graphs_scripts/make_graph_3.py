import os
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from matplotlib.patches import Patch

# Dimension configuration
IEEE_WIDTH = 3
IEEE_HEIGHT = 2.65

plt.rcParams.update({
    'figure.figsize': (IEEE_WIDTH, IEEE_HEIGHT),
    'figure.constrained_layout.use': True,
    'font.size': 9,
    'axes.labelsize': 9,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'font.family': 'Times New Roman',
    'lines.linewidth': 0.6,
    'axes.linewidth': 0.5,
    'grid.linewidth': 0.3,
    'axes.axisbelow': True,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})

def create_triage_discrete_violin_bars(data_file_name, output_graph_file_name):
    output_graph_file_name.parent.mkdir(parents=True, exist_ok=True)
    if not data_file_name.exists():
        print(f"[-] Error: Data file not found at {data_file_name}")
        return

    # Loading and cleaning data
    df = pd.read_csv(data_file_name)
    df = df.dropna(subset=['polyglot type', 'triage_score', 'obfuscated']).copy()
    
    # Standardize strings
    df['obfuscated'] = df['obfuscated'].astype(str).str.strip().map({'True': 'Obfuscated', 'False': 'Clear'})
    df['polyglot type'] = df['polyglot type'].str.strip().str.capitalize()
    df['triage_score'] = pd.to_numeric(df['triage_score'], errors='coerce').astype(int)

    # 2. Drawing parameter settings
    poly_order = ['Original', 'Stack', 'Cavity', 'Zipper']
    custom_palette = {'Clear': '#9ecae1', 'Obfuscated': '#084594'}
    
    fig, ax = plt.subplots()

    # --- ADJUSTMENT: Reduced maximum width to bring columns horizontally closer together ---
    # By decreasing the width from 0.45 to 0.32, each violin becomes more slender and the columns are brought closer together.
    max_bar_width = 0.32 

    # Find the global maximum frequency to normalize the size of the bars
    counts_global = df.groupby(['polyglot type', 'obfuscated', 'triage_score']).size()
    max_freq = counts_global.max() if not counts_global.empty else 1

    # 3. Construction of the bidirectional histogram (discrete violin)
    for x_idx, poly_type in enumerate(poly_order):
        sub_df = df[df['polyglot type'] == poly_type]
        ax.axvline(x=x_idx, color='#cccccc', linestyle='-', linewidth=0.5, zorder=1)

        for score in range(1, 11):
            # Left side: Clear (Values ​​subtracted from the X coordinate)
            clear_cnt = len(sub_df[(sub_df['triage_score'] == score) & (sub_df['obfuscated'] == 'Clear')])
            scale_clear = (clear_cnt / max_freq) * max_bar_width
            if clear_cnt > 0:
                ax.barh(score, scale_clear, left=x_idx - scale_clear, height=0.68, 
                        color=custom_palette['Clear'], edgecolor='black', linewidth=0.3, zorder=2)
                
            # Right side: Obfuscated (Values added to the X coordinate)
            obf_cnt = len(sub_df[(sub_df['triage_score'] == score) & (sub_df['obfuscated'] == 'Obfuscated')])
            scale_obf = (obf_cnt / max_freq) * max_bar_width
            if obf_cnt > 0:
                ax.barh(score, scale_obf, left=x_idx, height=0.68, 
                        color=custom_palette['Obfuscated'], edgecolor='black', linewidth=0.3, zorder=2)

    # 4. Fine adjustments of axes and IEEE-style grid
    ax.set_xticks(range(len(poly_order)))
    ax.set_xticklabels(poly_order)
    ax.set_yticks(range(1, 11))
    ax.set_ylim(0.4, 10.6)
    ax.set_xlim(-0.45, len(poly_order) - 0.55)

    ax.set_xlabel("Polyglot Strategy")
    ax.set_ylabel("Triage Dynamic Score (1-10)")
    ax.grid(axis='y', linestyle='--', alpha=0.4)

    # 5. ADJUSTMENT: Horizontal legend extracted FROM the graph (at the top)
    legend_elements = [
        Patch(facecolor=custom_palette['Clear'], edgecolor='black', linewidth=0.3, label='Clear'),
        Patch(facecolor=custom_palette['Obfuscated'], edgecolor='black', linewidth=0.3, label='Obfuscated')
    ]
    
    # It is positioned above the chart box using bbox_to_anchor
    ax.legend(
        handles=legend_elements,
        loc='lower center',
        bbox_to_anchor=(0.5, 1.02), 
        ncol=2, 
        frameon=True,
        facecolor='white', 
        edgecolor='black',
        framealpha=0.9, 
        fontsize=9,
        handletextpad=0.4,
        columnspacing=1.0,
        borderpad=0.25
    )

    # 6. Save vector graphic
    script_dir = Path(__file__).resolve().parent
    output_path = script_dir / output_graph_file_name
    plt.savefig(output_path, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"[+] Success: Discrete violin plot saved at {output_path}")

if __name__ == '__main__':
    # Path configuration
    script_dir = Path(__file__).resolve().parent
    data_csv = script_dir.parent / "results.csv"
    output_pdf = script_dir.parent / "graphs" / "3_triage_score_discrete_violin.pdf"
    
    create_triage_discrete_violin_bars(data_csv, output_pdf)