# pdf-polyglot-forge

A research-oriented toolkit for generating PDF polyglots that embed Bash, Python, and Ruby payloads. This project provides multiple merging strategies (prepend, append, middle injection) and supports clean formatting and header preservation. Designed for digital forensics, malware analysis research, and polyglot study—not for malicious use.

> ⚠️ **WARNING / DISCLAIMER** > This repository contains **live malware samples** inside the `PoC` directory used strictly for academic research and evaluation. The malicious files are stored inside password-protected `.zip` archives to prevent accidental execution.
> **The password for all malware zip files is: `infected`**

---

## 📂 Directory Structure

The repository is organized to support both the generation of polyglots and the reproduction of the experimental data presented in our research:

* **`make_pdf_polyglot.py`**: The core Python script used to inject payloads into PDF files using different structural positions.
* **`PoC/`**: Contains the Proof of Concept malware samples (`.sh`, `.rb`, `.py` threats like Mirai, Trojan Ruby, BeaverTail, etc.) and the base benign `sample.pdf` used for the injections.
* **`automated_task_scripts/`**: A suite of helper scripts (`bash` and `python`) used to automate the batch generation of polyglots, verify their syntax (`check_polyglots_syntax.sh`), and package them safely (`create_zips.sh`).
* **`generate_graphs/`**: Contains the experimental dataset (`NEW_PDF_tests.csv`) and the Python scripts (`generate_graph_X.py`) used to plot the detection rate charts featured in the paper. The outputs are saved in the `graphs/` subfolder.

---

## ⚙️ How it Works: `make_pdf_polyglot.py`

The main tool takes a benign PDF and a payload script (Bash, Python, or Ruby) and merges them into a single valid polyglot file. The tool supports three distinct injection techniques to test static analysis evasion:

### Arguments
* `--input`: Path to the base PDF file.
* `--keep`: Path to the payload file you want to embed (`.py`, `.rb`, `.sh`).
* `--output`: Name of the generated polyglot PDF.
* `--start`: Injects the payload at the **beginning** of the file (before the PDF header).
* `--middle`: Injects the payload deep inside the file, logically placed **in the middle** of the PDF objects.
* *(Default)*: If neither `--start` nor `--middle` is specified, the payload is appended at the **end** of the file (after the `%%EOF` trailer).
* `--verbose`: Enables detailed logging output.

### Usage Examples

**1. End Injection (Default)**
Appends the payload after the PDF trailer.
```bash
python make_pdf_polyglot.py --input PoC/sample.pdf --keep PoC/reverse_shell_python.py --output polyglot_end.pdf
