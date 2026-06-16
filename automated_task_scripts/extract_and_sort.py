import os
import shutil
import pyzipper
from pathlib import Path

ZIP_PASSWORD = b"infected"

EXTENSION_MAP = {
    '.py': 'python',
    '.sh': 'bash',
    '.js': 'javascript'
}

def process_malware_zips():
    # 1. Get absolute paths for the directories based on the script location
    # __file__ is the current script. .parent is 'automated_task_scripts'. .parent.parent is 'experiments'
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent
    
    zips_dir = base_dir / "malware_zips"
    malware_dir = base_dir / "malware"

    if not zips_dir.exists():
        print(f"[-] Error: Directory not found: {zips_dir}")
        return

    print(f"[*] Scanning ZIPs in: {zips_dir.name}/")

    # 2. Iterate through each ZIP file in the zips_dir
    for zip_path in zips_dir.glob("*.zip"):
        print(f"\n[*] Proccesing: {zip_path.name}")
        
        try:
            with pyzipper.AESZipFile(zip_path, 'r') as zf:
                zf.setpassword(ZIP_PASSWORD)
                
                # get_the zip file list 
                file_list = zf.namelist()
                
                if not file_list:
                    print(f"  [!] {zip_path.name} file is empty.")
                    continue
                elif len(file_list) > 1:
                    print(f"  [!] Warning: {zip_path.name} contains multiple files. Only the first will be extracted.")

                target_filename = file_list[0]
                
                # Extract the file to the zips_dir (it will be moved later)
                extracted_file_path = Path(zf.extract(target_filename, path=zips_dir))
                
                # 3. Get the file extension and determine the destination folder
                file_extension = extracted_file_path.suffix.lower()
                
                if file_extension in EXTENSION_MAP:
                    lang_folder = EXTENSION_MAP[file_extension]
                    destination_dir = malware_dir / lang_folder / "original"
                    
                    # Ensure the destination folder exists
                    destination_dir.mkdir(parents=True, exist_ok=True)
                    
                    final_path = destination_dir / extracted_file_path.name

                    if os.path.exists(final_path):
                        print(f"[!] WARNING: file '{final_path}' already exists.")
                        extracted_file_path.unlink()  # Remove the extracted file to avoid confusion
                        print(f"  [-] The extracted file from {zip_path.name} has been deleted to prevent overwriting.")
                    else:
                    
                        
                        # Move and overwrite if it already exists
                        shutil.move(str(extracted_file_path), str(final_path))
                        
                        # Show the relative path for a cleaner console output
                        print(f"  [+] Extracted and moved to: malware/{lang_folder}/original/{final_path.name}")
                else:
                    print(f"  [!] Unknown extension '{file_extension}'. The file remained in {zips_dir.name}/")
                    
        except RuntimeError as e:
            if 'Bad password' in str(e):
                print(f"  [-] Error: Incorrect password for {zip_path.name}")
            else:
                print(f"  [-] Execution error in {zip_path.name}: {e}")
        except pyzipper.BadZipFile:
            print(f"  [-] Error: {zip_path.name} is not a valid ZIP file or it is corrupted.")
        except Exception as e:
            print(f"  [-] Unexpected error with {zip_path.name}: {e}")

if __name__ == "__main__":
    process_malware_zips()