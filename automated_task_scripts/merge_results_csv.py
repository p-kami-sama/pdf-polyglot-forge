import os
import json
import csv
from pathlib import Path
from datetime import datetime

def consolidate_results():
    # Path resolution
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent 
    
    vt_dir = base_dir / "results_virustotal"
    triage_dir = base_dir / "results_triage"
    output_csv = base_dir / "results.csv"

    # Dict to hold combined data, keyed by SHA256 for easy merging
    combined_data = {}


    # 1. Read VirusTotal Results
    if vt_dir.exists():
        for json_file in vt_dir.rglob("*_report.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                try:
                    vt_json = json.load(f)
                    
                    # Extract SHA256 (commonly found in meta -> file_info -> sha256)
                    sha256 = vt_json.get("meta", {}).get("file_info", {}).get("sha256", "")
                    

                    
                    if not sha256:
                        # Fallback: Try to extract analysis ID "f-{hash}-{timestamp}"
                        analysis_id = vt_json.get("data", {}).get("id", "")
                        if analysis_id.startswith("f-"):
                            sha256 = analysis_id.split("-")[1]

                    if not sha256:
                        print(f"  [!] No SHA256 found in {json_file.name}")
                        continue

                    attrs = vt_json.get("data", {}).get("attributes", {})
                    stats = attrs.get("stats", {})
                    
                    # Convert UNIX timestamp from VT to ISO 8601 format (same as Triage)
                    vt_date_raw = attrs.get("date")
                    if vt_date_raw:
                        vt_date = datetime.utcfromtimestamp(vt_date_raw).strftime('%Y-%m-%dT%H:%M:%SZ')
                    else:
                        vt_date = ""
                    
                    # Extract polyglot type from the parent folder name 
                    poly_type = json_file.parent.name 

                    # Clean the filename to obtain the base name and extension
                    # Remove the '_report.json' suffix (since you renamed them earlier)
                    clean_filename = json_file.name.replace("_report.json", "")
                    
                    # Separate extension and base name
                    if '.' in clean_filename:
                        name_part, ext = clean_filename.rsplit('.', 1)
                    else:
                        name_part, ext = clean_filename, ''

                    # The 'name' will be the base name
                    name = name_part.replace(f"_{poly_type}", "")


                    combined_data[sha256] = {
                        "name": name,
                        "file type": ext,
                        "polyglot type": poly_type,
                        "sha256": sha256,
                        "vt_malicious": stats.get("malicious", ""),
                        "vt_suspicious": stats.get("suspicious", ""),
                        "vt_undetected": stats.get("undetected", ""),
                        "vt_harmless": stats.get("harmless", ""),
                        "vt_timeout": stats.get("timeout", ""),
                        "vt_confirmed_timeout": stats.get("confirmed-timeout", ""),
                        "vt_failure": stats.get("failure", ""),
                        "vt_type_unsupported": stats.get("type-unsupported", ""),
                        "vt_date": vt_date,
                        "triage_score": "",
                        "triage_date": "",

                        "obfuscated": False,    # Mark as non-obfuscated
                    }

                except Exception as e:
                    print(f"  [x] Error reading {json_file.name}: {e}")
    else:
        print(f"[-] Warning: Directory  {vt_dir} not found")



    print("[*] Starting the collection of Triage results...")
    # 2. Read Triage results 
    if triage_dir.exists():
        for json_file in triage_dir.rglob("*_triage_report.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                try:
                    triage_json = json.load(f)
                    sha256 = triage_json.get("sha256", "")
                    
                    if not sha256:
                        print(f"  [!] SHA256 not found in {json_file.name}")
                        continue
                        
                    # If Triage analyzed a file that VT didn't analyze (or if VT failed), we create it
                    if sha256 not in combined_data:
                        poly_type = json_file.parent.name
                        clean_filename = json_file.name.replace("_report.json", "")
                        
                        if '.' in clean_filename:
                            name_part, ext = clean_filename.rsplit('.', 1)
                        else:
                            name_part, ext = clean_filename, ''
                        
                        name = name_part.replace(f"_{poly_type}", "")
                        
                        combined_data[sha256] = {
                            "name": name,
                            "file type": ext,
                            "polyglot type": poly_type,
                            "sha256": sha256,
                            "vt_malicious": "", "vt_suspicious": "", "vt_undetected": "", 
                            "vt_harmless": "", "vt_timeout": "", "vt_confirmed_timeout": "", 
                            "vt_failure": "", "vt_type_unsupported": "", "vt_date": "",
                            "triage_score": "", "triage_date": ""
                        }

                    # Fill in the specific Triage data
                    combined_data[sha256]["triage_score"] = triage_json.get("score", "")
                    combined_data[sha256]["triage_date"] = triage_json.get("completed", "")

                except Exception as e:
                    print(f"  [x] Error reading {json_file.name}: {e}")
    else:
        print(f"[-] Warning: Directory  {triage_dir} not found")




    # We repeat the same process for obfuscated samples, but we mark them as "obfuscated" in the final CSV.
    vt_dir = base_dir / "results_virustotal_obfuscated"
    triage_dir = base_dir / "results_triage_obfuscated"


    # 1. Read VirusTotal Results
    if vt_dir.exists():
        for json_file in vt_dir.rglob("*_report.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                try:
                    vt_json = json.load(f)
                    
                    # Extract SHA256 (commonly found in meta -> file_info -> sha256)
                    sha256 = vt_json.get("meta", {}).get("file_info", {}).get("sha256", "")

                    
                    if not sha256:
                        # Fallback: Try to extract analysis ID "f-{hash}-{timestamp}"
                        analysis_id = vt_json.get("data", {}).get("id", "")
                        if analysis_id.startswith("f-"):
                            sha256 = analysis_id.split("-")[1]

                    if not sha256:
                        print(f"  [!] No SHA256 found in {json_file.name}")
                        continue

                    attrs = vt_json.get("data", {}).get("attributes", {})
                    stats = attrs.get("stats", {})
                    
                    # Convert UNIX timestamp from VT to ISO 8601 format (same as Triage)
                    vt_date_raw = attrs.get("date")
                    if vt_date_raw:
                        vt_date = datetime.utcfromtimestamp(vt_date_raw).strftime('%Y-%m-%dT%H:%M:%SZ')
                    else:
                        vt_date = ""

                    # Extract polyglot type from the parent folder name 
                    poly_type = json_file.parent.name 

                    # Clean the filename to obtain the base name and extension
                    # Remove the '_report.json' suffix (since you renamed them earlier)
                    clean_filename = json_file.name.replace("_report.json", "")
                    
                    # Separate extension and base name
                    if '.' in clean_filename:
                        name_part, ext = clean_filename.rsplit('.', 1)
                    else:
                        name_part, ext = clean_filename, ''

                    # The 'name' will be the base name
                    name = name_part.replace(f"_{poly_type}", "")


                    combined_data[sha256] = {
                        "name": name,
                        "file type": ext,
                        "polyglot type": poly_type,
                        "sha256": sha256,
                        "vt_malicious": stats.get("malicious", ""),
                        "vt_suspicious": stats.get("suspicious", ""),
                        "vt_undetected": stats.get("undetected", ""),
                        "vt_harmless": stats.get("harmless", ""),
                        "vt_timeout": stats.get("timeout", ""),
                        "vt_confirmed_timeout": stats.get("confirmed-timeout", ""),
                        "vt_failure": stats.get("failure", ""),
                        "vt_type_unsupported": stats.get("type-unsupported", ""),
                        "vt_date": vt_date,
                        "triage_score": "",
                        "triage_date": "",

                        "obfuscated": True,     # Mark as obfuscated
                    }

                except Exception as e:
                    print(f"  [x] Error reading {json_file.name}: {e}")
    else:
        print(f"[-] Warning: Directory  {vt_dir} not found")



    print("[*] Starting the collection of Triage results...")
    # 2. Read Triage results 
    if triage_dir.exists():
        for json_file in triage_dir.rglob("*_triage_report.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                try:
                    triage_json = json.load(f)
                    sha256 = triage_json.get("sha256", "")
                    
                    if not sha256:
                        print(f"  [!] SHA256 not found in {json_file.name}")
                        continue
                        
                    # If Triage analyzed a file that VT didn't analyze (or if VT failed), we create it
                    if sha256 not in combined_data:
                        poly_type = json_file.parent.name
                        clean_filename = json_file.name.replace("_report.json", "")
                        
                        if '.' in clean_filename:
                            name_part, ext = clean_filename.rsplit('.', 1)
                        else:
                            name_part, ext = clean_filename, ''
                        
                        name = name_part.replace(f"_{poly_type}", "")
                        
                        combined_data[sha256] = {
                            "name": name,
                            "file type": ext,
                            "polyglot type": poly_type,
                            "sha256": sha256,
                            "vt_malicious": "", "vt_suspicious": "", "vt_undetected": "", 
                            "vt_harmless": "", "vt_timeout": "", "vt_confirmed_timeout": "", 
                            "vt_failure": "", "vt_type_unsupported": "", "vt_date": "",
                            "triage_score": "", "triage_date": ""
                        }

                    # Fill in the specific Triage data
                    combined_data[sha256]["triage_score"] = triage_json.get("score", "")
                    combined_data[sha256]["triage_date"] = triage_json.get("completed", "")

                except Exception as e:
                    print(f"  [x] Error reading {json_file.name}: {e}")
    else:
        print(f"[-] Warning: Directory  {triage_dir} not found")








    # 3. Write the final CSV
    headers = [
        "name", "file type", "polyglot type", "obfuscated", "sha256",
        "vt_malicious", "vt_suspicious", "vt_undetected", "vt_harmless",
        "vt_timeout", "vt_confirmed_timeout", "vt_failure", "vt_type_unsupported", "vt_date",
        "triage_score", "triage_date", 
    ]

    print(f"\n[*] Writing the merged data to {output_csv.name}...")
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        
        # Guardar todas las filas
        for row in combined_data.values():
            writer.writerow(row)

    print(f"[+] Process completed successfully. {len(combined_data)} unique samples analyzed.")

if __name__ == "__main__":
    consolidate_results()