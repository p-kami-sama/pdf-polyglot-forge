import os
import csv
import time
import json
import requests
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
# Delay to avoid burst rate limits on Triage API (5 seconds is safe)
DELAY_SECONDS = 5
TRIAGE_API_URL_BASE = "https://tria.ge/api/v0/samples"

EXTENSIONS = ["bash", "javascript", "python"]

def get_api_key(key_path):
    """Read the Triage API key from the specified text file."""
    if not key_path.exists():
        print(f"[!] Error: API key file not found at {key_path}")
        exit(1)
    with open(key_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def load_already_analyzed(csv_filepath):
    """Return a set of filenames that have already been fully analyzed."""
    analyzed = set()
    if not csv_filepath.exists():
        return analyzed

    with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get("Analysis_Status") == "reported":
                analyzed.add(row["Filename"])
    return analyzed

def log_final_result(csv_filepath, filename, p_type, sample_id, status, score):
    """Save the final analysis result into a CSV."""
    file_exists = csv_filepath.exists()
    
    with open(csv_filepath, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            # Triage uses a 'Score' out of 10 instead of engine counts
            writer.writerow(["Filename", "Polyglot_Type", "Triage_Sample_ID", "Analysis_Status", "Triage_Score"])
        writer.writerow([filename, p_type, sample_id, status, score])

def process_triage_results(responses_dir, results_dir, api_key_path):
    
    # Get the API key
    api_key = get_api_key(api_key_path)
    headers = {"Authorization": f"Bearer {api_key}"}

    # 2. Iterate through extensions
    for ext in EXTENSIONS:
        ext_responses_dir = responses_dir / ext
        upload_log_path = ext_responses_dir / "uploaded_triage_samples_log.csv"
        
        ext_results_dir = results_dir / ext
        ext_results_dir.mkdir(parents=True, exist_ok=True)
        final_results_path = ext_results_dir / "final_triage_results.csv"
        
        if not upload_log_path.exists():
            print(f"[-] Skipping {ext.upper()}: Upload log not found at {upload_log_path}.")
            continue
            
        already_analyzed = load_already_analyzed(final_results_path)
        
        print(f"\n========================================")
        print(f"[*] Fetching results for: {ext.upper()}")
        print(f"========================================")

        # 3. Read the IDs generated during the upload phase
        with open(upload_log_path, 'r', newline='', encoding='utf-8') as upload_csv:
            reader = csv.DictReader(upload_csv)
            
            for row in reader:
                filename = row["Filename"]
                p_type = row["Polyglot_Type"]
                sample_id = row["Triage_Sample_ID"]
                upload_status = row["Status"]
                
                # Skip failed uploads or already analyzed files
                if upload_status != "Success":
                    continue
                if filename in already_analyzed:
                    print(f"  [~] Skipping '{filename}' (Already fully analyzed).")
                    continue
                
                print(f"  [>] Fetching ID '{sample_id}' for '{filename}'...")
                
                # Query the sample ID directly
                url = f"{TRIAGE_API_URL_BASE}/{sample_id}"
                
                try:
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("status", "unknown")
                        
                        # In Triage, "reported" means the analysis is completely finished
                        if status == "reported":
                            score = data.get("score", 0)
                            
                            print(f"    [+] Completed! Malicious Score: {score}/10")
                            log_final_result(final_results_path, filename, p_type, sample_id, status, score)
                            
                            # Fetch detailed summary if you want extra info (signatures, MITRE ATT&CK)
                            # We make a secondary call to the /summary endpoint for the full report
                            summary_url = f"{url}/summary"
                            summary_resp = requests.get(summary_url, headers=headers)
                            
                            if summary_resp.status_code == 200:
                                summary_data = summary_resp.json()
                                # Save the full report JSON
                                report_dir = ext_results_dir / p_type
                                report_dir.mkdir(parents=True, exist_ok=True)
                                with open(report_dir / f"{filename}_triage_report.json", "w", encoding="utf-8") as f:
                                    json.dump(summary_data, f, indent=4)
                                    
                        elif status in ["pending", "running"]:
                            print(f"    [-] Still processing in Sandbox (Status: {status}).")
                            log_final_result(final_results_path, filename, p_type, sample_id, status, "N/A")
                            
                    elif response.status_code == 429:
                        print(f"    [!] Error 429: Rate limit exceeded. Halting script.")
                        return 
                        
                    elif response.status_code == 404:
                        print(f"    [x] Error 404: Sample not found in Triage. Might have been deleted.")
                        log_final_result(final_results_path, filename, p_type, sample_id, "not_found", "N/A")
                        
                    else:
                        print(f"    [x] HTTP Error {response.status_code}: {response.text}")
                        
                except Exception as e:
                    print(f"    [x] Exception: {e}")

                # Rate limiting sleep
                print(f"    [z] Waiting {DELAY_SECONDS} seconds...")
                time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    print("[*] Starting Triage results retrieval...")
        # 1. Resolve paths
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent
    api_key_path = script_dir / "api_keys" / "triage_api_key.txt"
    
    responses_dir = base_dir / "responses_triage" # Read IDs from here
    results_dir = base_dir / "results_triage"     # Save results here
    process_triage_results(responses_dir, results_dir, api_key_path)


    responses_dir = base_dir / "responses_triage_obfuscated" # Read IDs from here
    results_dir = base_dir / "results_triage_obfuscated"     # Save results here

    process_triage_results(responses_dir, results_dir, api_key_path)

    print("\n[*] Process finished.")