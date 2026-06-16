import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path

# Dimension configuration
def setup_ieee_format():
    sns.set_theme(style="ticks") 
    
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman'],
        'font.size': 8,
        'axes.labelsize': 8,
        'xtick.labelsize': 7,
        'ytick.labelsize': 7,
        'axes.titlesize': 9,
        'axes.linewidth': 0.5,
        
        # Grid and tick settings
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'xtick.major.size': 3.5,
        'ytick.major.size': 3.5,
        'xtick.major.width': 0.5,
        'ytick.major.width': 0.5,
        'xtick.bottom': True,
        'ytick.left': True,
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
    })

def custom_linear_hist2d(**kwargs):

    data = kwargs.pop("data")
    x_col = kwargs.pop("x")
    y_col = kwargs.pop("y")
    vmax = kwargs.pop("vmax")
    max_vt = kwargs.pop("max_vt")
    
    kwargs.pop("color", None)
    kwargs.pop("label", None)
    
    ax = plt.gca()
    
    bx = np.arange(0, max_vt + 2, 1)
    by = np.arange(0, 12)
    norm = mcolors.PowerNorm(gamma=0.4, vmin=0, vmax=vmax)
    
    ax.hist2d(
        data[x_col], 
        data[y_col], 
        bins=[bx, by], 
        cmap="Blues", 
        norm=norm
    )



def generate_2d_hist_grid(csv_path, output_path):
    input_csv = Path(csv_path)
    if not input_csv.exists():
        print(f"[-] Error: No se encontró {input_csv}")
        return

    df = pd.read_csv(input_csv)
    df['polyglot type'] = df['polyglot type'].fillna('unknown').str.capitalize()
    df['triage_score'] = pd.to_numeric(df['triage_score'], errors='coerce')

    order_tech = ['Original', 'Stack', 'Cavity', 'Zipper']
    df['polyglot type'] = pd.Categorical(df['polyglot type'], categories=order_tech, ordered=True)

    max_samples = df.groupby(['polyglot type', 'vt_malicious', 'triage_score'], observed=True).size().max()
    max_vt = int(df['vt_malicious'].max())

    setup_ieee_format()

    ratio_aspect = (max_vt + 2) / 12.0
    g = sns.FacetGrid(
        df, 
        col="polyglot type", 
        col_wrap=1, 
        height=1.2, 
        aspect=ratio_aspect,
        sharex=True, 
        sharey=True
    )

    g.map_dataframe(
        custom_linear_hist2d, 
        x='vt_malicious', 
        y='triage_score', 
        vmax=max_samples,
        max_vt=max_vt
    )

    g.set_titles(col_template="{col_name}", fontweight='bold')
    g.set_axis_labels('VT Detections', 'Triage Score')

    g.set(xlim=(0, max_vt ), ylim=(0, 11))
    
    for ax in g.axes.flat:
        ax.xaxis.set_major_locator(plt.MaxNLocator(5))

    for i, ax in enumerate(g.axes.flat):
        if i < 2: 
            ax.tick_params(labelbottom=False)

    # Global colorbar
    power_norm = mcolors.PowerNorm(gamma=0.4, vmin=0, vmax=max_samples)
    sm = plt.cm.ScalarMappable(cmap="Blues", norm=power_norm)
    sm.set_array([])
    
    g.fig.subplots_adjust(right=0.82, hspace=0.4, wspace=0.1)
    
    cbar_ax = g.fig.add_axes([0.85, 0.25, 0.01, 0.5]) 
    cbar = g.fig.colorbar(sm, cax=cbar_ax)
    
    cbar.set_label('Number of Samples', size=8)
    cbar.ax.tick_params(labelsize=7)

    plt.savefig(output_path, format='pdf', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Graph saved to: {output_path}")




if __name__ == "__main__":
    # 1. Path configuration
    script_dir = Path(__file__).resolve().parent
    csv_file = script_dir.parent / "results.csv"
    pdf_file = script_dir.parent / "graphs" / "4_vt_triage_heatmap.pdf"
    
    generate_2d_hist_grid(str(csv_file), str(pdf_file))
    