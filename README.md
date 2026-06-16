# pdf-polyglot-forge

A research-oriented toolkit for generating PDF polyglots that embed Bash, JavaScript, and Python payloads. This project provides multiple merging strategies and supports clean formatting and header preservation. Designed for digital forensics, malware analysis research, and polyglot study, not for malicious use.

> ⚠️ **WARNING / DISCLAIMER** > This repository contains **live malware samples** inside the `PoC` directory used strictly for academic research and evaluation. The malicious files are stored inside password-protected `.zip` archives to prevent accidental execution.
> **The password for all malware zip files is: `infected`**

---
## 📂 Directory Structure

The repository is organized to support both the generation of polyglots and the reproduction of the experimental data presented in our research:

* **`make_pdf_polyglot.py`**: The core Python script used to inject payloads into PDF files using different structural positions.
* **`automated_task_scripts/`**: A suite of helper scripts `python` used to automate the batch generation of polyglots, verify their syntax (`check_polyglots_syntax.sh`).
* **`generate_graphs/`**: Contains the experimental dataset (`NEW_PDF_tests.csv`) and the Python scripts (`generate_graph_X.py`) used to plot the detection rate charts featured in the paper. The outputs are saved in the `graphs/` subfolder.

---

## ⚙️ How it Works: `make_pdf_polyglot.py`

The main tool takes a benign PDF and a payload script (Bash, JavaScript, or Python) and merges them into a single valid polyglot file. The tool supports three distinct injection techniques to test static analysis evasion:

### Positional Arguments
* `base_file`: Path to the base file (e.g., original PDF).
* `payload_file`: Path to the payload file (e.g., JavaScript).
* `output_file`: Path for the resulting output file.


### Options

* `-h`, `--help`: Show a help message and exit.
* `-o`, `--obfuscate`: Hides the presence of the payload in the PDF structure by obfuscating the injected code.
* `-t`, `--type` :  Injection strategy to use. Valid options: {stack,cavity,zipper,original}. Original won't modify the structure of the script, just can apply obfuscation if the flag -o is set.
* `-v`, `--verbose`: Enables detailed logging output.

### Usage Examples
```bash
python merge_pdf.py input.pdf payload.js result.pdf --type cavity --obfuscate -v
```
