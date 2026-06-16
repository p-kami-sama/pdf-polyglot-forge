import os
import csv
import time
import json
import requests
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
# API rate limit for the free tier: 4 requests per minute. (1 request every 15 seconds + 1 for safety)
DELAY_SECONDS = 16 
EXTENSIONS = ["bash", "javascript", "python"]

def get_api_key(key_path):
    if not key_path.exists():
        print(f"[!] Error: Archivo de API key no encontrado en {key_path}")
        exit(1)
    with open(key_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def load_already_analyzed(csv_filepath):
    """Returns a set with the filenames that have already had a completed analysis."""
    analyzed = set()
    if not csv_filepath.exists():
        return analyzed

    with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get("Analysis_Status") == "completed":
                analyzed.add(row["Filename"])
    return analyzed

def log_final_result(csv_filepath, filename, p_type, vt_id, status, malicious, undetected):
    """Keep the final result in a new CSV."""
    file_exists = csv_filepath.exists()
    
    with open(csv_filepath, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Filename", "Polyglot_Type", "VT_Analysis_ID", "Analysis_Status", "Malicious_Engines", "Undetected_Engines"])
        writer.writerow([filename, p_type, vt_id, status, malicious, undetected])


def process_results(responses_dir, results_dir, api_key_path):
    
    api_key = get_api_key(api_key_path)
    headers = {"x-apikey": api_key}

    for ext in EXTENSIONS:

        # Read paths (responses)
        ext_responses_dir = responses_dir / ext
        upload_log_path = ext_responses_dir / "uploaded_samples_log.csv"
        
        # Write paths (results)
        ext_results_dir = results_dir / ext
        ext_results_dir.mkdir(parents=True, exist_ok=True)
        final_results_path = ext_results_dir / "final_analysis_results.csv"


        if not upload_log_path.exists():
            print(f"[-] Skipping {ext.upper()}: No upload log found in {upload_log_path}.")
            continue
            
        already_analyzed = load_already_analyzed(final_results_path)


        
        print(f"\n========================================")
        print(f"[*] Getting results for: {ext.upper()}")
        print(f"========================================")

        # Read previous upload log to get VT Analysis IDs
        with open(upload_log_path, 'r', newline='', encoding='utf-8') as upload_csv:
            reader = csv.DictReader(upload_csv)
            
            for row in reader:
                filename = row["Filename"]
                p_type = row["Polyglot_Type"]
                analysis_id = row["VT_Analysis_ID"]
                upload_status = row["Status"]
                
                # Ignore those that failed to upload or those we have already analyzed successfully
                if upload_status != "Success":
                    continue
                if filename in already_analyzed:
                    print(f"  [~] Skipping '{filename}' (Analysis already downloaded previously).")
                    continue
                
                print(f"  [>] Consulting ID of '{filename}'...")
                url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
                
        
                try:
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        attributes = data.get("data", {}).get("attributes", {})
                        status = attributes.get("status", "unknown")
                        
                        if status == "completed":
                            stats = attributes.get("stats", {})
                            malicious = stats.get("malicious", 0)
                            undetected = stats.get("undetected", 0)
                            
                            print(f"    [+] Completed: {malicious} engines detected it as malware.")
                            log_final_result(final_results_path, filename, p_type, analysis_id, status, malicious, undetected)
                            
                            # Save the complete report JSON in case you need deep data later
                            report_dir = ext_results_dir / p_type
                            report_dir.mkdir(parents=True, exist_ok=True)
                            with open(report_dir / f"{filename}_report.json", "w", encoding="utf-8") as f:
                                json.dump(data, f, indent=4)
                                
                        elif status in ["queued", "in-progress"]:
                            print(f"    [-] Already processing in VT (Status: {status}).")
                            # We store it as incomplete to not lose the trail, but we don't add it to 'already_analyzed'
                            log_final_result(final_results_path, filename, p_type, analysis_id, status, "N/A", "N/A")
                            
                    elif response.status_code == 429:
                        print(f"    [!] HTTP Error 429: API Rate Limit exceeded. Stopping the script.")
                        return # Abort to protect the API key from being blocked.
                        
                    else:
                        print(f"    [x] HTTP Error{response.status_code}: {response.text}")
                        
                except Exception as e:
                    print(f"    [x] Exception: {e}")

                # Pause to respect API rate limits
                print(f"    [z] Waiting {DELAY_SECONDS} seconds...")
                time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    
    print("[*] Starting download of VirusTotal results...")    
    
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent
    api_key_path = script_dir / "api_keys" / "virustotal_api_key.txt"
    
    responses_dir = base_dir / "responses_virustotal"
    results_dir = base_dir / "results_virustotal"
    process_results(responses_dir, results_dir, api_key_path)


    responses_dir = base_dir / "responses_virustotal_obfuscated"
    results_dir = base_dir / "results_virustotal_obfuscated"
    process_results(responses_dir, results_dir, api_key_path)

    print("\n[*] Proceso finalizado.")