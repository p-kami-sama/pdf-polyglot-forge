import os
import subprocess
import csv
from pathlib import Path

# polyglot types
POLYGLOT_TYPES = ["stack", "zipper", "cavity"]
# Extensions to process
EXTENSIONS = ["bash", "javascript", "python"]

def analyze_output_for_syntax(stdout, stderr, ext):
    """
    Evaluate the output of merge_pdf.py to determine if the polyglot parsing is correct.
    """
    output_lower = (stdout + stderr).lower()
    
    if "error" in output_lower or "failed" in output_lower or "traceback" in output_lower or "[WARNING]".lower() in output_lower:
        return "Failure"

    return "Success"



def generate_polyglots():
    # 1. Resolve base routes dynamically
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent
    
    merge_pdf_script = base_dir / "merge_pdf.py"
    sample_pdf = base_dir / "sample.pdf"
    malware_dir = base_dir / "malware"

    # Verify that the main files exist
    if not merge_pdf_script.exists() or not sample_pdf.exists():
        print("[-] Error: merge_pdf.py or sample.pdf not found in the main directory.")
        return

    # 2. Iterate over each extension and process the original files
    for ext in EXTENSIONS:
        ext_dir = malware_dir / ext
        original_dir = ext_dir / "original"
        
        if not original_dir.exists():
            print(f"[*] Saltando {ext}: No existe la carpeta original.")
            continue

        print(f"\n[*] Procesando payloads de {ext}...")
        
        # CSV file to store the results (file_name, polyglot_type, pdf_syntax_check)
        csv_path = ext_dir / f"syntax_check_results.csv"
        
        # Open the CSV in write mode
        with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["file_name", "polyglot_type", "syntax_check"])
            
            # 3. Iterate over each original file in the original_dir
            for original_file in original_dir.glob("*"):
                if not original_file.is_file():
                    continue
                
                # 4. Create the 3 variants for each file
                for p_type in POLYGLOT_TYPES:
                    # Name of the output file: FILE_NAME_cavity, FILE_NAME_stack, etc.
                    # output_name = f"{original_file.name}_{p_type}"
                    output_name = f"{original_file.stem}_{p_type}{original_file.suffix}"

                    output_dir = ext_dir / p_type
                    output_file = output_dir / output_name
                    
                    # Ensure that the destination folder exists (cavity, stack, zipper)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Build the command to execute
                    # Pass the absolute paths to avoid working directory issues
                    command = [
                        "python3", # Use python3 explicitly to avoid issues with different environments
                        str(merge_pdf_script),
                        str(sample_pdf),
                        str(original_file),
                        str(output_file),
                        "--type", p_type
                    ]
                    
                    print(f"  [>] Generando {p_type} para {original_file.name}...")
                    print(f"      Comando: {' '.join(command)}")
                    
                    try:
                        # Run the merge_pdf.py script and capture the output
                        result = subprocess.run(
                            command, 
                            capture_output=True, 
                            text=True, 
                        )
                        
                        # Determine if the syntactic analysis was correct based on the output
                        syntax_status = analyze_output_for_syntax(result.stdout, result.stderr, ext)
                        
                        # Write the row in the CSV
                        writer.writerow([output_file.name, p_type, syntax_status])
                        
                    except Exception as e:
                        print(f"  [x] Error executing the command for {output_name}: {e}")
                        writer.writerow([original_file.name, p_type, f"Execution error: {e}"])

        print(f"[+] Syntax results saved in: {csv_path.relative_to(base_dir)}")






    # repeat the process to create obfuscated versions of the generated polyglots
    POLYGLOT_TYPES.append("original")  # Add "original" to the list of polyglot types for obfuscation
    malware_obfuscated_dir = base_dir / "malware_obfuscated"    
    malware_obfuscated_dir.mkdir(parents=True, exist_ok=True)   # Create the malware_obfuscated folder if it does not exist

    # Create obfuscated versions of the generated polyglots
    for ext in EXTENSIONS:

        original_dir = malware_dir / ext / "original"     # ../malware/bash/original, ../malware/javascript/original, etc.
        
        ext_dir = malware_obfuscated_dir / ext  # ../malware_obfuscated/bash, ../malware_obfuscated/javascript, etc.


        ext_dir.mkdir(parents=True, exist_ok=True)
        
        if not original_dir.exists():
            print(f"[*] Skipping {ext}: The original folder does not exist.")
            continue

        print(f"\n[*] Processing {ext} payloads to make obfuscated versions...")
        
        # CSV file to store the results (file_name, polyglot_type, pdf_syntax_check)
        csv_path = ext_dir / f"syntax_check_results.csv"
        
        # Open the CSV in write mode
        with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["file_name", "polyglot_type", "syntax_check"])
            
            # 3. Iterate over each original file in the original_dir
            for original_file in original_dir.glob("*"):
                if not original_file.is_file():
                    continue
                
                # 4. Create the 3 variants for each file
                for p_type in POLYGLOT_TYPES:
                    # Name of the output file: FILE_NAME_cavity, FILE_NAME_stack, etc.
                    output_name = f"{original_file.stem}_{p_type}{original_file.suffix}"

                    output_dir = ext_dir / p_type
                    output_file = output_dir / output_name
                    
                    # Ensure that the destination folder exists (cavity, stack, zipper)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Build the command to execute
                    # Pass the absolute paths to avoid working directory issues
                    command = [
                        "python3", # Use python3 explicitly to avoid issues with different environments
                        str(merge_pdf_script),
                        str(sample_pdf),
                        str(original_file),
                        str(output_file),
                        "--type", p_type,
                        "-o"    # Flag to indicate that we want an obfuscated version
                    ]
                    
                    print(f"  [>] Generating {p_type} for {original_file.name}...")
                    print(f"      Command: {' '.join(command)}")
                    
                    try:
                        # Run the merge_pdf.py script and capture the output
                        result = subprocess.run(
                            command, 
                            capture_output=True, 
                            text=True, 
                        )
                        
                        # Determine if the syntax analysis was successful based on the output
                        syntax_status = analyze_output_for_syntax(result.stdout, result.stderr, ext)
                        
                        # Write the row in the CSV
                        writer.writerow([output_file.name, p_type, syntax_status])
                        
                    except Exception as e:
                        print(f"  [x] Error generating {p_type} for {output_name}: {e}")
                        writer.writerow([original_file.name, p_type, f"Execution error: {e}"])

        print(f"[+] Syntax results saved in: {csv_path.relative_to(base_dir)}")







if __name__ == "__main__":
    generate_polyglots()