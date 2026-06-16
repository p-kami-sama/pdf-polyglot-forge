To replicate the experiment, you must run the following scripts in the given order.

First, write your own API keys in the corresponding .txt files inside "api_keys" folder.

Then, run the following scripts from within this directory in the given order.

Keep in mind that this may take several hours or even several days, depending on the type of API key you have and the maximum number of queries per day.

Extract all the files within the ZIP archive from the "malware_zips" folder using the password `infected` and save them in the "malware" subdirectory according to their extension.
> python3 extract_and_sort.py

Create polyglot files from the original malware in the "malware" folder using "sample.pdf" as the PDF file using the "make_pdf_polyglot.py" script
> python3 create_polyglots.py

Send all files in the "malware" directory to VirusTotal slowly and save the responses in the "responses_virustotal" directory.
> python3 upload_files_virustotal.py

It slowly retrieves the VirusTotal scan results and saves them in the "results_virustotal" directory.
> python3 get_virustotal_results

Send all files in the "malware" directory to Triage slowly and save the responses in the "responses_triage" directory.
> python3 upload upload_files_triage.py

It slowly retrieves the Triage scan results and saves them in the "results_virustotal" directory.
> python3 get_triage_results.py

Create file "results.csv" where the results from VirusTotal and Triage are collected.
> python3 merge_results_csv.py