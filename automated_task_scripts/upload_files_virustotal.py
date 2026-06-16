import os
import csv
import time
import json
import requests
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
# VirusTotal Public API allows 4 requests per minute.
# 60 seconds / 4 requests = 15 seconds. Adding 1 sec for safety.
DELAY_SECONDS = 16 
VT_API_URL = "https://www.virustotal.com/api/v3/files"

EXTENSIONS = ["bash", "javascript", "python"]
POLYGLOT_TYPES = ["original", "cavity", "stack", "zipper"]

def get_api_key(key_path):
    """Read the API key from the specified text file."""
    if not key_path.exists():
        print(f"[!] Error: API key file not found at {key_path}")
        exit(1)
    with open(key_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def load_processed_files(csv_filepath):
    """
    Read the CSV log to return a set of filenames that have already 
    been successfully uploaded, avoiding duplicate work.
    """
    processed = set()
    if not csv_filepath.exists():
        return processed

    with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get("Status") == "Success":
                processed.add(row["Filename"])
    
    return processed

def log_to_csv(csv_filepath, filename, polyglot_type, vt_id, status):
    """Append the upload result to the CSV file."""
    file_exists = csv_filepath.exists()
    
    with open(csv_filepath, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write headers if the file is being created
        if not file_exists:
            writer.writerow(["Filename", "Polyglot_Type", "VT_Analysis_ID", "Status"])
        writer.writerow([filename, polyglot_type, vt_id, status])

def process_uploads(malware_dir, responses_dir, api_key_path):
    
    
    # Get the API key
    api_key = get_api_key(api_key_path)
    headers = {"x-apikey": api_key}

    # 2. Iterate through each programming language (extension)
    for ext in EXTENSIONS:
        ext_malware_dir = malware_dir / ext
        ext_responses_dir = responses_dir / ext
        
        # Ensure the results base directory for this extension exists
        ext_responses_dir.mkdir(parents=True, exist_ok=True)
        
        # Path for the CSV log inside the extension folder
        csv_log_path = ext_responses_dir / "uploaded_samples_log.csv"
        
        # Load already processed files to avoid re-uploading
        processed_files = load_processed_files(csv_log_path)
        
        print(f"\n========================================")
        print(f"[*] Processing extension: {ext.upper()}")
        print(f"========================================")

        # 3. Iterate through each polyglot type folder
        for p_type in POLYGLOT_TYPES:
            target_folder = ext_malware_dir / p_type
            result_target_folder = ext_responses_dir / p_type
            
            if not target_folder.exists():
                print(f"  [-] Skipping {p_type}/ (Folder not found)")
                continue
            
            # Ensure the specific result folder exists (e.g., results_virustotal/python/cavity)
            result_target_folder.mkdir(parents=True, exist_ok=True)
            
            print(f"\n  [*] Entering folder: {p_type}/")
            
            # 4. Upload each file inside the folder
            for sample_path in target_folder.glob("*"):
                if not sample_path.is_file():
                    continue
                
                filename = sample_path.name
                
                if filename in processed_files:
                    print(f"    [~] Skipping '{filename}' (Already uploaded)")
                    continue
                
                print(f"    [>] Uploading '{filename}'...")
                
                try:
                    with open(sample_path, 'rb') as f:
                        files = {'file': (filename, f)}
                        response = requests.post(VT_API_URL, headers=headers, files=files)
                    
                    if response.status_code == 200:
                        # Success: Extract ID and save JSON
                        data = response.json()
                        analysis_id = data.get("data", {}).get("id", "UNKNOWN_ID")
                        
                        print(f"      [+] Success! Analysis ID: {analysis_id}")
                        log_to_csv(csv_log_path, filename, p_type, analysis_id, "Success")
                        
                        # Save the raw JSON response to the results folder
                        json_result_path = result_target_folder / f"{filename}_vt_upload_response.json"
                        with open(json_result_path, "w", encoding="utf-8") as json_file:
                            json.dump(data, json_file, indent=4)
                            
                    elif response.status_code == 429:
                        # Rate Limit Exceeded
                        print(f"      [!] HTTP 429: Rate limit exceeded. Halting to protect the API key.")
                        print(f"      [!] Please wait a few minutes before running the script again.")
                        return # Exit the function completely
                        
                    else:
                        # Other HTTP errors
                        print(f"      [x] Error {response.status_code}: {response.text}")
                        log_to_csv(csv_log_path, filename, p_type, "N/A", f"HTTP_{response.status_code}")
                
                except Exception as e:
                    print(f"      [x] Exception during upload: {e}")
                    log_to_csv(csv_log_path, filename, p_type, "N/A", f"Exception: {e}")

                # 5. Mandatory sleep to respect the 4 requests/minute limit
                print(f"      [z] Sleeping for {DELAY_SECONDS} seconds to respect API limits...")
                time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    print("[*] Starting VirusTotal upload sequence...")
    
    # 1. Resolve dynamic paths based on the script location
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent
    api_key_path = script_dir / "api_keys" / "virustotal_api_key.txt"

    malware_dir = base_dir / "malware"
    responses_dir = base_dir / "responses_virustotal"
    process_uploads(malware_dir, responses_dir, api_key_path)


    malware_dir = base_dir / "malware_obfuscated"
    responses_dir = base_dir / "responses_virustotal_obfuscated"

    process_uploads(malware_dir, responses_dir, api_key_path)


    print("\n[*] All tasks finished.")