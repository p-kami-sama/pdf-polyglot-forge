import pandas as pd
import numpy as np
from pathlib import Path

def create_latex_table(file_path):
    # 1. Load and clear data
    data_file = Path(file_path)
    if not data_file.exists():
        print("[-] Error: 'results.csv' not found in the current directory.")
        return

    df = pd.read_csv(data_file)
    df.columns = [c.strip() for c in df.columns]
    
    df['file type'] = df['file type'].str.strip().str.upper()
    df['polyglot type'] = df['polyglot type'].str.strip().str.lower()
    df['obfuscated'] = df['obfuscated'].astype(str).str.strip().map({'True': 'Yes', 'False': 'No'})
    df['triage_score'] = pd.to_numeric(df['triage_score'], errors='coerce')

    # Language mapping
    lang_map = {'SH': 'Bash', 'JS': 'JavaScript', 'PY': 'Python'}
    df['file type'] = df['file type'].map(lang_map)
    df = df.dropna(subset=['file type', 'polyglot type', 'obfuscated'])

    # 2. Prepare VirusTotal metrics
    vt_denom_cols = ['vt_malicious', 'vt_suspicious', 'vt_undetected', 'vt_harmless', 
                     'vt_timeout', 'vt_confirmed_timeout', 'vt_failure', 'vt_type_unsupported']
    for col in vt_denom_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['vt_total_valid'] = df[vt_denom_cols].sum(axis=1)
    df_vt = df[df['vt_total_valid'] > 0].copy()
    df_vt['Detection_PCT'] = (df_vt['vt_malicious'] / df_vt['vt_total_valid']) * 100

    # 3. Prepare Triage metrics (Normalization from 1-10 to 0%-100%)
    df_triage = df.dropna(subset=['triage_score']).copy()
    df_triage['Triage_PCT'] = ((df_triage['triage_score'] - 1) / (10 - 1)) * 100

    # Row and column structure
    strategies = ['original', 'stack', 'cavity', 'zipper']
    languages = ['Bash', 'JavaScript', 'Python']

    def calculate_means(target_df, value_column):
        means = {}
        for lang in languages + ['Global']:
            means[lang] = {}
            for obf in ['No', 'Yes']:
                means[lang][obf] = {}
                for strat in strategies:
                    if lang == 'Global':
                        sub = target_df[(target_df['polyglot type'] == strat) & 
                                        (target_df['obfuscated'] == obf)]
                    else:
                        sub = target_df[(target_df['file type'] == lang) & 
                                        (target_df['polyglot type'] == strat) & 
                                        (target_df['obfuscated'] == obf)]
                    means[lang][obf][strat] = sub[value_column].mean() if len(sub) > 0 else np.nan
        return means

    vt_means = calculate_means(df_vt, 'Detection_PCT')
    triage_means = calculate_means(df_triage, 'Triage_PCT')

    # 4. Building LaTeX code
    tex =  "\\begin{table*}[t]\n"
    tex += "  \\centering\n"
    tex += "  \\caption{Comprehensive Evasion Analysis: Static vs. Dynamic Evaluation Across Polyglot Configurations}\n"
    tex += "  \\label{tab:malware_detection_results}\n"
    tex += "  \\begin{tabular}{llcccc|cccc}\n"
    tex += "    \\toprule\n"
    # First header row with unified blocks
    tex += "    & & \\multicolumn{4}{c}{\\textbf{VirusTotal Detection Rate}} & \\multicolumn{4}{c}{\\textbf{Normalized Triage Score}} \\\\\n"
    tex += "    \\cmidrule(lr){3-6} \\cmidrule(lr){7-10}\n"
    # Second header row with structural strategies
    tex += "    \\textbf{Prog. Lang.} & \\textbf{Obfuscated} & \\textbf{Original} & \\textbf{Stack} & \\textbf{Cavity} & \\textbf{Zipper} & \\textbf{Original} & \\textbf{Stack} & \\textbf{Cavity} & \\textbf{Zipper} \\\\\n"
    tex += "    \\midrule\n"
    
    display_langs = languages + ['Global']
    for i, lang in enumerate(display_langs):
        if lang == 'Global':
            tex += "    \\midrule\n    \\bfseries Global & No"
        else:
            tex += f"    \\multirow{{2}}{{*}}{{{lang}}} & No"
            
        # --- Row: Obfuscated = No ---
        # VirusTotal Block
        for strat in strategies:
            val = vt_means[lang]['No'][strat]
            tex += f" & {val:.2f}\\%" if pd.notnull(val) else " & --"
        # Triage Block
        for strat in strategies:
            val = triage_means[lang]['No'][strat]
            tex += f" & {val:.2f}\\%" if pd.notnull(val) else " & --"
        tex += " \\\\\n"
        
        # --- Row: Obfuscated = Yes ---
        if lang == 'Global':
            tex += "    \\bfseries        & Yes"
        else:
            tex += "                 & Yes"
            
        # VirusTotal Block
        for strat in strategies:
            val = vt_means[lang]['Yes'][strat]
            tex += f" & {val:.2f}\\%" if pd.notnull(val) else " & --"
        # Triage Block
        for strat in strategies:
            val = triage_means[lang]['Yes'][strat]
            tex += f" & {val:.2f}\\%" if pd.notnull(val) else " & --"
        tex += " \\\\\n"
        
        # Separators between language blocks
        if lang != 'Global' and i < len(languages) - 1:
            tex += "    \\cmidrule(lr){1-10}\n"
            
    tex += "    \\bottomrule\n"
    tex += "  \\end{tabular}\n"
    tex += "\\end{table*}\n"

    print(tex)

if __name__ == '__main__':
    # 1. Path configuration
    script_dir = Path(__file__).resolve().parent
    data_csv = script_dir.parent / "results.csv"
    create_latex_table(data_csv)
