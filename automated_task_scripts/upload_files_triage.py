import os
import csv
import time
import json
import requests
from pathlib import Path

# ==========================================
# CONFIGURACIÓN
# ==========================================
# Allowed rate on free accounts in Triage
DELAY_SECONDS = 5
TRIAGE_API_URL = "https://tria.ge/api/v0/samples"

EXTENSIONS = ["bash", "javascript", "python"]
POLYGLOT_TYPES = ["original", "cavity", "stack", "zipper"]

def get_api_key(key_path):
    """Read the Triage API key from the file."""
    if not key_path.exists():
        print(f"[!] Error: API key file not found in {key_path}")
        exit(1)
    with open(key_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def load_processed_files(csv_filepath):
    """Returns a set with the filenames that have already been successfully uploaded."""
    processed = set()
    if not csv_filepath.exists():
        return processed

    with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get("Status") == "Success":
                processed.add(row["Filename"])
    
    return processed

def log_to_csv(csv_filepath, filename, polyglot_type, sample_id, status):
    """Saves the upload record in the corresponding CSV."""
    file_exists = csv_filepath.exists()
    
    with open(csv_filepath, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Filename", "Polyglot_Type", "Triage_Sample_ID", "Status"])
        writer.writerow([filename, polyglot_type, sample_id, status])

def process_triage_uploads(malware_dir, responses_dir, api_key_path):
    
    # Obtain API key and configure headers
    api_key = get_api_key(api_key_path)
    headers = {"Authorization": f"Bearer {api_key}"}

    # 2. Iterate over the extensions (python, bash, javascript)
    for ext in EXTENSIONS:
        ext_malware_dir = malware_dir / ext
        ext_responses_dir = responses_dir / ext
        
        # Create the base responses folder if it doesn't exist
        ext_responses_dir.mkdir(parents=True, exist_ok=True)
        
        # File for control (Log) for this extension
        csv_log_path = ext_responses_dir / "uploaded_triage_samples_log.csv"
        processed_files = load_processed_files(csv_log_path)
        
        print(f"\n========================================")
        print(f"[*] Processing extension: {ext.upper()}")
        print(f"========================================")

        # 3. Iterate over the polyglot types
        for p_type in POLYGLOT_TYPES:
            target_folder = ext_malware_dir / p_type
            response_target_folder = ext_responses_dir / p_type
            
            if not target_folder.exists():
                print(f"  [-] Skipping {p_type}/ (Folder not found)")
                continue
            
            # Create the subfolder in responses_triage (e.g., responses_triage/python/cavity)
            response_target_folder.mkdir(parents=True, exist_ok=True)
            
            print(f"\n  [*] Entrando en la carpeta: {p_type}/")
            
            # 4. Upload each file from the folder
            for sample_path in target_folder.glob("*"):
                # Ignore internal control folders and .csv files
                if not sample_path.is_file() or sample_path.suffix == ".csv":
                    continue
                
                filename = sample_path.name
                
                if filename in processed_files:
                    print(f"    [~] Skipping '{filename}' (Already uploaded previously)")
                    continue
                
                print(f"    [>] Uploading '{filename}' to Triage...")
                
                try:
                    with open(sample_path, 'rb') as f:
                        # Triage expects the file under the key 'file'
                        files = {'file': (filename, f)}
                        response = requests.post(TRIAGE_API_URL, headers=headers, files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        # Triage returns the ID in the 'id' field of the JSON root
                        sample_id = data.get("id", "UNKNOWN_ID")
                        
                        
                        print(f"      [+] Success! Sample ID: {sample_id}")
                        log_to_csv(csv_log_path, filename, p_type, sample_id, "Success")
                        
                        # Keep a copy of the JSON response in the corresponding folder
                        json_result_path = response_target_folder / f"{filename}_triage_response.json"
                        with open(json_result_path, "w", encoding="utf-8") as json_file:
                            json.dump(data, json_file, indent=4)
                            
                    elif response.status_code == 429:
                        print(f"      [!] HTTP 429: Request limit reached. Aborting to protect the account.")
                        return 
                        
                    else:
                        print(f"      [x] Error {response.status_code}: {response.text}")
                        log_to_csv(csv_log_path, filename, p_type, "N/A", f"HTTP_{response.status_code}")
                
                except Exception as e:
                    print(f"      [x] Exception during upload: {e}")
                    log_to_csv(csv_log_path, filename, p_type, "N/A", f"Exception: {e}")

                # 5. Delay
                time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    print("[*] Initiating the upload sequence to Hatching Triage...")
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent

    api_key_path = script_dir / "api_keys" / "triage_api_key.txt"    

    malware_dir = base_dir / "malware"
    responses_dir = base_dir / "responses_triage"
    process_triage_uploads(malware_dir, responses_dir, api_key_path)


    malware_dir = base_dir / "malware_obfuscated"
    responses_dir = base_dir / "responses_triage_obfuscated"
    process_triage_uploads(malware_dir, responses_dir, api_key_path)

    print("\n[*] All uploads have been completed.")