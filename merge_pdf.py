import os
import re

import argparse
import sys
import base64

import pypdf as pypdf
import ast
import subprocess
import logging

import marshal
import zlib
import textwrap




# return the file extension in lowercase, including the dot (e.g., '.pdf', '.py')
def get_extension(path: str) -> str:
    return os.path.splitext(path)[1].lower()

# format_parsing
# structural_ensambling
#   stack
#   cavity
#   zipper
# active_manipulation


# Analyze the PDF structure and the payload file to determine if they are suitable for the specified polyglot type, and extract necessary information for the merging process.
def format_parsing(pdf_file_path: str, payload_file_path: str, polyglot_type: str = 'stack', verbose: bool = False):
    polyglot_type = polyglot_type.lower()
    
    if get_extension(pdf_file_path) != '.pdf':
        print("Invalid PDF file type. The input file must have a .pdf extension.")
        return False
    elif get_extension(payload_file_path) not in ['.sh', '.py', '.rb', '.js' ]:
        print("Invalid payload file type. Must be a shell script (.sh), Python script (.py), Ruby script (.rb), or JavaScript script (.js).")
        return False
    
    if verbose:
        print(f"PDF file: {pdf_file_path}")
        print(f"Payload file: {payload_file_path}")
        print(f"Polyglot type: {polyglot_type}")
    matches = False
    pdf_data = None

    if polyglot_type == 'stack' and os.path.getsize(payload_file_path) > 1000:
        print("The payload file is too large for stack polyglot, In some viewers the PDF content may not be rendered. Consider using cavity or zipper polyglot for larger payloads.")

    
    
    if payload_file_path.endswith('.py'):
        with open(payload_file_path, 'rb') as pdf_f:
            pdf_data = pdf_f.read()
            if b'\x00' in pdf_data:
                print("[WARNING] The PDF file has a null byte, so the Python code probably doesn't work. Please try another PDF.")
            elif verbose:
                print("No null byte found in the PDF file, continuing with the process.")
    

    if polyglot_type == 'cavity':            
        # Search for a suitable point between PDF objects

        with open(pdf_file_path, 'rb') as pdf_f:
            pdf_data = pdf_f.read()
            matches = list(re.finditer(rb'\nendobj[\r]?\n', pdf_data))
            
            return bool(matches) 
            # Return True if matches found, False otherwise.
            # we will handle the error in the calling function to avoid stopping the whole process if no matches are found,
            # since cavity polyglot is more likely to fail with some PDFs due to their structure.
            # The rest of the code will be able to continue and create a stack or zipper polyglot instead.
        
    else:
        return True
    




def structural_ensambling(pdf_file_path: str, payload_file_path: str, output_file_path: str, polyglot_type: str = 'stack', verbose: bool = False, obfuscate: bool = False):

    with open(pdf_file_path, 'rb') as pdf_f:
        pdf_data = pdf_f.read()
            
        
    if polyglot_type == 'stack':
        structural_ensambling_stack(pdf_data, payload_file_path, output_file_path, obfuscate)

    # it's necessary to create the cavity in the PDF before assembling the final polyglot,
    #  since we need to divide the PDF into two parts for the cavity method,
    #  and this division is based on the structure of the PDF itself (specifically, the positions of the objects in the PDF).
    elif polyglot_type == 'cavity':
        matches = list(re.finditer(rb'\nendobj[\r]?\n', pdf_data))


        # Middle point between PDF objects for insertion
        insert_pos = matches[len(matches) // 2].end()

        # Divide the PDF into two parts:
        pdf_part1 = pdf_data[:insert_pos]
        pdf_part2 = pdf_data[insert_pos:]


        structural_ensambling_cavity(pdf_part1, pdf_part2, payload_file_path, output_file_path, verbose, obfuscate, insert_pos)

    
    elif polyglot_type == 'zipper':
        structural_ensambling_zipper(pdf_data, payload_file_path, output_file_path, verbose, obfuscate)





# Append the payload before the PDF
def structural_ensambling_stack(pdf_data: bytes, payload_file_path: str, output_file_path: str, obfuscate: bool = False):

    with open(payload_file_path, 'rb') as payload_f:
        payload_data = payload_f.read()

    if obfuscate:
        payload_data = obfuscate_payload(payload_data, get_extension(payload_file_path))

    with open(output_file_path, 'wb') as output_f:   # Creamos el archivo de salida en modo binario

        if get_extension(payload_file_path) == '.sh':
            output_f.write(payload_data) 
        
            # PDF is enclosed in a multi-line comment    
            comment_word = "comment_to_ignore_pdf_content"
            output_f.write(f"\n: << '{comment_word}'\n".encode("utf-8"))
            output_f.write(pdf_data)
            output_f.write(f"\n{comment_word}\n".encode("utf-8"))

        elif get_extension(payload_file_path) == '.rb':
            output_f.write(payload_data)  
            output_f.write("\n=begin\n".encode())
            output_f.write(pdf_data)
            output_f.write("\n=end\n".encode())
        
        elif get_extension(payload_file_path) == '.py':
            encoding = '''# coding: iso-8859-1 -*-'''
            output_f.write(encoding.encode("iso-8859-1"))
            output_f.write(b'\n')
            output_f.write(payload_data)
            output_f.write(b'\nr"""\n')
            output_f.write(pdf_data)
            output_f.write(b'"""\n')


        elif get_extension(payload_file_path) == '.js':
            output_f.write(payload_data)
            output_f.write(b'\n/*\n')
            output_f.write(pdf_data)
            output_f.write(b'*/\n')



# create a cavity in the middle of the PDF creating an unreferenced object to insert the payload there
def structural_ensambling_cavity(pdf_part1: bytes, pdf_part2: bytes, payload_file_path: str, output_file_path: str, verbose: bool = False, obfuscate: bool = False, insert_pos = None):
        
    with open(payload_file_path, 'rb') as payload_f:
        payload_data = payload_f.read()

    if obfuscate:
        payload_data = obfuscate_payload(payload_data, get_extension(payload_file_path))


    if verbose:
        print(f"Inserting script at position {insert_pos} in the PDF file.")

    if get_extension(payload_file_path) == '.sh':

        if verbose:
            print(f"Inserting shell script at position {insert_pos} in the PDF file.")
        
        comment_word = "comment_to_ignore_pdf_content"
        
        # The first part of the PDF is enclosed in a multi-line comment
        bash_payload = f": << '{comment_word}'\n".encode("utf-8")
        bash_payload += pdf_part1
        bash_payload += f"\n{comment_word}\n".encode("utf-8")

        bash_payload += payload_data  # Add the Bash script as bytes
        
        bash_payload += f"\n: << '{comment_word}'\n".encode("utf-8")
        bash_payload += pdf_part2
        bash_payload += f"\n{comment_word}\n".encode("utf-8")
        

        # Ensamblar el PDF final con Bash embebido
        with open(output_file_path, "wb") as f:
            f.write(bash_payload)



    elif get_extension(payload_file_path) == '.rb':    # Ruby payload:

        shebang = b""
        encoding_line = b""

        # Dividir por líneas solo para analizar encabezados
        lines = payload_data.split(b"\n")

        idx = 0

        # 1) Ruby scrpts may start with a shebang, if it exists we want to preserve it at the very top of the file.
        if lines and lines[0].startswith(b"#!"):
            shebang = lines[0] + b"\n"
            idx = 1

        # 2) Look for an optional encoding line
        encoding_patterns = [
            b"# encoding:",
            b"# -*- coding:",
            b"# coding:",
        ]
        # extract encoding line if it exists, we want to preserve it right after the shebang
        if idx < len(lines):
            line = lines[idx].lower()
            if any(pat in line for pat in encoding_patterns):
                encoding_line = lines[idx] + b"\n"
                idx += 1

        # rest of script after shebang + encoding
        rest_of_script = b"\n".join(lines[idx:]) + b"\n"

        ruby_payload = b""

        ruby_payload += shebang
        ruby_payload += encoding_line
        
        ruby_payload += b"=begin\n"
        ruby_payload += pdf_part1
        ruby_payload += b"\n=end\n"

        ruby_payload += rest_of_script
        ruby_payload += b"\n"

        ruby_payload  += b"\n=begin\n"
        ruby_payload += pdf_part2
        ruby_payload += b"\n=end\n"

        # Ensamblate final PDF with Ruby code embedded
        with open(output_file_path, "wb") as f:
            f.write(ruby_payload)


    elif get_extension(payload_file_path) == '.py':    # Python payload
        # this is more complex because we need to ensure the encoding is correct and that the PDF content is properly encapsulated in a way that doesn't break the Python syntax
        encoding = "# coding: iso-8859-1 -*-\n"

        # The PDF is completely encapsulated inside a raw string
        python_payload  = encoding.encode("iso-8859-1")
        python_payload += b"r\"\"\"\n"
        python_payload += pdf_part1
        python_payload += b"\n\"\"\"\n"

        # Python code from the payload file
        # python_payload += str(payload_data).encode("iso-8859-1")
        python_payload += payload_data
        python_payload += b"\n"

        python_payload += b"\nr\"\"\"\n"
        python_payload += pdf_part2
        python_payload += b"\n\"\"\"\n"

        # Ensamblate final PDF with Python code embedded
        with open(output_file_path, "wb") as f:
            f.write(python_payload)


    elif get_extension(payload_file_path) == '.js':

        js_payload = b"/*\n"
        js_payload += pdf_part1
        js_payload += b"\n*/\n"

        js_payload += payload_data
        js_payload += b"\n/*\n"
        js_payload += pdf_part2
        js_payload += b"\n*/\n"

        # Ensamblate final PDF with JavaScript code embedded
        with open(output_file_path, "wb") as f:
            f.write(js_payload)




# Append the payload at the end of the PDF
def structural_ensambling_zipper(pdf_data: bytes, payload_file_path: str, output_file_path: str = 'stack', verbose: bool = False, obfuscate: bool = False):

    with open(payload_file_path, 'rb') as payload_f:
        payload_data = payload_f.read()

    if obfuscate:
        payload_data = obfuscate_payload(payload_data, get_extension(payload_file_path))

    if get_extension(payload_file_path) == '.sh':
        # extract shebang if it exists to preserve it at the top of the file,
        # otherwise the script may not be recognized as a valid shell script by some environments

        with open(output_file_path, 'wb') as output_f:
            comment_word = "comment_to_ignore_pdf_content"
            output_f.write(f": << '{comment_word}'\n".encode())
            output_f.write(pdf_data)
            output_f.write(f"\n{comment_word}\n".encode())
            output_f.write(payload_data)
            output_f.write(b"\nexit\n")

    elif get_extension(payload_file_path) == '.rb':

        with open(output_file_path, 'wb') as output_f:

            shebang = b""
            encoding_line = b""

            lines = payload_data.split(b"\n")

            idx = 0

            if lines and lines[0].startswith(b"#!"):
                shebang = lines[0] + b"\n"
                idx = 1

            encoding_patterns = [
                b"# encoding:",
                b"# -*- coding:",
                b"# coding:",
            ]

            if idx < len(lines):
                line = lines[idx].lower()
                if any(pat in line for pat in encoding_patterns):
                    encoding_line = lines[idx] + b"\n"
                    idx += 1

            rest_of_script = b"\n".join(lines[idx:]) + b"\n"


            # Payload Ruby:
            ruby_headers = b""

            # Prepend shebang + encoding si existen
            ruby_headers += shebang
            ruby_headers += encoding_line
    
            output_f.write(ruby_headers)
            output_f.write("\n=begin\n".encode())
            output_f.write(pdf_data)
            output_f.write("\n=end\n".encode())
            output_f.write(rest_of_script)

    elif get_extension(payload_file_path) == '.py':
        with open(output_file_path, 'wb') as output_f:
            encoding = '''# coding: iso-8859-1 -*-'''
            output_f.write(encoding.encode("iso-8859-1"))
            output_f.write(b'\nr"""\n')
            output_f.write(pdf_data)
            output_f.write(b'"""\n')
            output_f.write(payload_data)



    if get_extension(payload_file_path) == '.js':

        with open(output_file_path, 'wb') as output_f:
            output_f.write("/*\n".encode())
            output_f.write(pdf_data)
            output_f.write("\n*/\n".encode())
            output_f.write(payload_data)





def active_manipulation(pdf_file_path: str, output_file_path: str, verbose: bool = False):
    # 1.Reading the original and the polyglot PDF files as binary data
    if not os.path.exists(pdf_file_path) or not os.path.exists(output_file_path):
        print(f"Error: {pdf_file_path} or {output_file_path} not found.")
        return

    with open(pdf_file_path, 'rb') as f:
        sample_data = f.read()

    with open(output_file_path, 'rb') as f:
        polyglot_data = bytearray(f.read())


    # 2. Extract all objects (X Y obj ... endobj) from the original pdf
    # Use re.DOTALL is crucial for reading line breaks and internal binary bytes
    # '.*?' ensures that it stops at the first 'endobj' it encounters
    obj_pattern = re.compile(rb'(\d+) (\d+) obj.*?endobj', re.DOTALL)
    
    objects_to_find = {}
    for match in obj_pattern.finditer(sample_data):
        obj_id = int(match.group(1))
        obj_content = match.group(0)
        objects_to_find[obj_id] = obj_content
    if verbose:
        print(f"{len(objects_to_find)} objects were extracted for tracing in the original PDF.")

    # 3. Find the new location of those objects in the modified PDF
    new_offsets = {}
    for obj_id, obj_content in objects_to_find.items():
        # find() will return the exact offset where the byte sequence begins
        offset = polyglot_data.find(obj_content)
        if offset != -1:
            new_offsets[obj_id] = offset
        else:
            print(f"Warning: The object {obj_id} was not found in the polyglot file.")


    # 4. Update the xref table in place
    if verbose:
        print("[*] Reconstructing table 'xref'...")
    
    # Find the start of the xref table and the trailer block
    xref_start = polyglot_data.rfind(b'\nxref\n')
    if xref_start == -1:
        # Some PDFs don't have the preceding line break before 'xref', so we try to find 'xref\n' directly
        xref_start = polyglot_data.rfind(b'xref\n')
    else:
        xref_start += 1 # Adjust the index so that it points exactly to the 'x'

    trailer_pos = polyglot_data.rfind(b'trailer', xref_start)
    
    if xref_start == -1 or trailer_pos == -1:
        print("Error: No classic 'xref' table or 'trailer' was detected. (Possible linearized PDF or with XRefStm)")
        return

    # Extract the exact block from the table
    xref_data = polyglot_data[xref_start:trailer_pos].splitlines(keepends=True)
    modified_xref_data = bytearray()
    
    current_obj_id = -1
    
    for line in xref_data:
        if line.startswith(b'xref'):
            modified_xref_data.extend(line)
            continue
            
        parts = line.split()
        
        # If it is the subsection header (e.g., "0 15")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            current_obj_id = int(parts[0])
            modified_xref_data.extend(line)
            continue
            
        # If it is a table entry (e.g. "0000000015 00000 n \r\n")
        if len(parts) >= 3 and len(parts[0]) == 10:
            if parts[2] == b'n' and current_obj_id in new_offsets:
                # Format the new offset to 10 required digits (PDF Spec)
                new_off_str = f"{new_offsets[current_obj_id]:010d}".encode('ascii')
                # We replaced ONLY the first 10 bytes to avoid breaking spaces or the \r\n
                new_line = new_off_str + line[10:]
                modified_xref_data.extend(new_line)
            else:
                # Keep 'f' (free) entries or those we don't find the same
                modified_xref_data.extend(line)
            
            current_obj_id += 1
            continue
            
        # Any other line (blank, etc.)
        modified_xref_data.extend(line)

    # Inject the corrected xref block into the modified data
    polyglot_data = polyglot_data[:xref_start] + modified_xref_data + polyglot_data[trailer_pos:]


    # Update the startxref pointer
    # When inserting text before the xref table, its offset also changed.
    # startxref_pos = polyglot_data.rfind(b'startxref')
    # if startxref_pos != -1:
    #     # We rewrite the end of the file with the new absolute pointer of xref
    #     new_eof = b'startxref\n' + str(xref_start).encode('ascii') + b'\n%%EOF\n'
    #     polyglot_data = polyglot_data[:startxref_pos] + new_eof
    

    # Update the startxref pointer
    # When inserting text before the xref table, its offset also changed.
    startxref_pos = polyglot_data.rfind(b'startxref')
    if startxref_pos != -1:
        # 1. Find the position of the next "%%EOF" 
        eof_pos = polyglot_data.find(b'%%EOF', startxref_pos)
        
        if eof_pos != -1:
            # 2. Calculate the index right after the "%%EOF" keyword (5 bytes)
            end_of_eof = eof_pos + 5
            
            # 3. Save all the extra bytes (payload of your polyglot) that come after
            trailing_data = polyglot_data[end_of_eof:]
            
            # 4. Crate a new section startxref
            # Don't forget that the PDF specification requires a newline after the startxref value,
            #  but we don't add a newline after %%EOF because we want to preserve the original
            #  trailing data as much as possible, which may already contain newlines.
            new_eof_section = b'startxref\n' + str(xref_start).encode('ascii') + b'\n%%EOF'
            
            # 5. Ensamblate the final PDF keeping the trailing data
            polyglot_data = polyglot_data[:startxref_pos] + new_eof_section + trailing_data
        else:
            # In case the PDF is malformed and doesn't have a %%EOF.
            new_eof_section = b'startxref\n' + str(xref_start).encode('ascii') + b'\n%%EOF\n'
            polyglot_data = polyglot_data[:startxref_pos] + new_eof_section


    # Save the final result
    with open(output_file_path, 'wb') as f:
        f.write(polyglot_data)
        




# Only checks the syntax of the PDF polyglot without executing it (to avoid running potentially malicious code during validation)
def structural_validation(output_file_path: str, payload_extension: str, verbose: bool = False):
    if not os.path.isfile(output_file_path):
        print(f"[ERROR] Output file {output_file_path} not found.")
        return False
    
    # Basic validation to check if the output file has the expected structure based on the payload type
    with open(output_file_path, 'rb') as f:
        polyglot_data = f.read()

    if verbose:
        print(f"\nStarting structural validation for {output_file_path} with payload type {payload_extension}...")
    try:
        logging.getLogger("pypdf").setLevel(logging.ERROR)  # to avoid verbose warnings from pypdf when parsing potentially malformed PDFs
        reader = pypdf.PdfReader(output_file_path)
        _ = len(reader.pages) > 0  # try to access pages to trigger parsing of the PDF structure
    except Exception as e:
        print(f"[WARNING] PyPDF failed to parse the PDF structure: {e}. The PDF may not be rendered correctly in some viewers.")

    if verbose:
        print("PDF structure seems valid based on PyPDF parsing.")



    if payload_extension == '.sh':
        try:
            # bash -n only checks the syntax of the script without executing it
            resultado = subprocess.run(
                ["bash", "-n", output_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if  len(resultado.stderr.decode()) != 0:
                print("[WARNING]: Structural validation failed for bash script payload.")
                return False
            elif verbose:
                print("Structural validation passed for bash script payload.")
            return True
        except Exception:
            print("[WARNING]: Structural validation failed for bash script payload.")
            return False


    elif payload_extension == '.rb':    
        try:
            # ruby -c checks the syntax of the Ruby script
            resultado = subprocess.run(
                ["ruby", "-c", output_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if len(resultado.stderr.decode()) != 0:
                print("[WARNING]: Structural validation failed for ruby script payload.")
                return False
            elif verbose:
                print("Structural validation passed for ruby script payload.")
            return True

        except Exception:
            print("[WARNING]: Structural validation failed for ruby script payload.")
            return False



    elif payload_extension == '.py':
        try:
            ast.parse(polyglot_data.decode("iso-8859-1"))
            if verbose:
                print("Structural validation passed for python script payload.")
            return True
        except Exception:
            print("[WARNING]: Structural validation failed for python script payload.")
            return False


    elif payload_extension == '.js':    
        try:
            # We use qjsc (the QuickJS compiler) to validate the syntax.
            # -e: exports to C (only compiles, does not execute)
            # -o os.devnull: discards the generated file; we only want the status code.
            resultado = subprocess.run(
                ["qjsc", "-e", "-o", os.devnull, output_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            result = resultado.returncode == 0
            if not result:
                print("[WARNING]: Structural validation failed for JavaScript payload (via QuickJS).")
            elif verbose:
                print("Structural validation passed for JavaScript payload (via QuickJS).")
                
            
            return result

        except FileNotFoundError:
            print("[WARNING]: 'qjsc' not found. Is QuickJS installed and added to PATH?")
            return False
        except Exception as e:
            print(f"[WARNING]: Error during QuickJS validation: {e}")
            return False



# Main function to merge PDF and payload based on the specified polyglot type
def merge_pdf(pdf_file_path: str, payload_file_path: str, output_file_path: str, polyglot_type: str = 'stack', verbose: bool = False, obfuscate: bool = False):
    polyglot_type = polyglot_type.lower()
    

    if polyglot_type not in ['stack', 'cavity', 'zipper', 'original']:
        raise ValueError(f"Invalid polyglot type. Must be 'stack', 'cavity', 'zipper', or 'original'. Type {polyglot_type} not recognized.")
    
    correct_format = format_parsing(pdf_file_path, payload_file_path, polyglot_type, verbose)
    if not correct_format:
        print("[ERROR] The PDF or payload file format is not correct for stack polyglot. Ensure the PDF is valid and the payload is a supported script type.")
        return
    
    
    structural_ensambling(pdf_file_path, payload_file_path,output_file_path, polyglot_type, verbose, obfuscate)
    

    active_manipulation(pdf_file_path, output_file_path, verbose)


    valid_polyglot = structural_validation(output_file_path, get_extension(payload_file_path), verbose)
    if valid_polyglot:
        print(f"{output_file_path} is a valid polyglot PDF/{get_extension(payload_file_path)[1:]} file.")
    else:
        print(f"[WARNING] {output_file_path} is a polyglot PDF/{get_extension(payload_file_path)[1:]} file but failed structural validation. It may not work correctly in all viewers or environments.")






def obfuscate_payload_bash(payload_data: bytes) -> bytes:

    source = payload_data.decode(
        "utf-8",
        errors="ignore"
    )

    # Remove shebanf
    if source.startswith("#!"):
        source = re.sub(
            r"^#!.*?\n",
            "",
            source,
            count=1
        )

    # Compress the source code using zlib with maximum compression level
    compressed = zlib.compress(
        source.encode("utf-8"),
        level=9
    )

    # Use base64 encoding
    encoded = base64.b64encode(
        compressed
    ).decode("ascii")


    # Bash loader that decodes and executes the payload at runtime
    loader = f"""#!/usr/bin/env bash
set -e
_PLD='{encoded}'
_TMPDIR="$(mktemp -d)"
_TMPFILE="$_TMPDIR/embedded.sh"
cleanup() {{
    rm -f "$_TMPFILE" 2>/dev/null || true
    rmdir "$_TMPDIR" 2>/dev/null || true
}}
trap cleanup EXIT INT TERM
printf '%s' "$_PLD" \\
| base64 -d \\
| python3 -c '
import sys
import zlib
sys.stdout.buffer.write(
    zlib.decompress(
        sys.stdin.buffer.read()
    )
)
' > "$_TMPFILE"
chmod +x "$_TMPFILE"
exec bash "$_TMPFILE" "$@"
"""

    return textwrap.dedent(
        loader
    ).encode("utf-8")



def obfuscate_payload_python(payload_data: bytes) -> bytes:

    code_object = compile(
        payload_data,
        "<payload>",
        "exec"
    )
    marshalled = marshal.dumps(code_object)
    compressed = zlib.compress(
        marshalled,
        level=9
    )
    encoded = base64.b85encode(compressed)

    loader = f'''
import base64
import marshal
import zlib
_PLD = {encoded!r}
CMPRSSD = base64.b85decode(_PLD)
marshalled = zlib.decompress(CMPRSSD)
cd = marshal.loads(marshalled)
globals_dict = {{"__name__": "__main__","__file__": "<embedded>"}}
exec(cd, globals_dict)
'''
    obfuscated_code = textwrap.dedent(loader)
    return obfuscated_code.encode("utf-8") # We encode the loader as bytes
    

def obfuscate_payload_javascript(payload_data: bytes) -> bytes:

    source = payload_data.decode(
        "utf-8",
        errors="ignore"
    )

    # Remove shebang
    if source.startswith("#!"):
        source = re.sub(
            r"^#!.*?\n",
            "",
            source,
            count=1
        )

    # Compress
    compressed = zlib.compress(
        source.encode("utf-8"),
        level=9
    )

    # Encode
    encoded = base64.urlsafe_b64encode(
        compressed
    ).decode("ascii")

    # Loader
    loader = f"""
const fs = require("fs");
const os = require("os");
const path = require("path");
const zlib = require("zlib");
const crypto = require("crypto");
const Module = require("module");
const _PLD = "{encoded}";
const compressed = Buffer.from(
    _PLD,
    "base64url"
);
const source = zlib
    .inflateSync(compressed)
    .toString("utf8");
const uniqueName =
    "embedded_" +
    crypto.randomBytes(8).toString("hex") +
    ".js";
const tempDir = fs.mkdtempSync(
    path.join(os.tmpdir(), "node_loader_")
);
const virtualFilename = path.join(
    tempDir,
    uniqueName
);
fs.writeFileSync(
    virtualFilename,
    source,
    "utf8"
);
const m = new Module(
    virtualFilename,
    module
);
m.filename = virtualFilename;
m.paths = Module._nodeModulePaths(
    path.dirname(virtualFilename)
);
function cleanup() {{
    try {{
        fs.unlinkSync(virtualFilename);
    }} catch {{}}
    try {{
        fs.rmdirSync(tempDir);
    }} catch {{}}
}}
process.on("exit", cleanup);
process.on("SIGINT", () => {{
    cleanup();
    process.exit(1);
}});
process.on("SIGTERM", () => {{
    cleanup();
    process.exit(1);
}});
m._compile(
    source,
    virtualFilename
);
"""

    return textwrap.dedent(
        loader
    ).encode("utf-8")






def obfuscate_payload(payload_data: bytes, payload_extension: str) -> bytes:
    if payload_extension == '.sh':
        return obfuscate_payload_bash(payload_data)
    
    elif payload_extension == '.py':
        return obfuscate_payload_python(payload_data)        

    elif payload_extension == '.js':
        return obfuscate_payload_javascript(payload_data)

    else:   # No obfuscation for unsupported types
        print('[WARNING] Obfuscation is not supported for this payload type. The payload will be injected without obfuscation.')
        return payload_data







def main():
    # 1. Initialize the parser
    parser = argparse.ArgumentParser(
        description="Script for manipulating polyglot/PDF files.",
        epilog="Usage example: python3 merge_pdf.py input.pdf payload.js result.pdf --type cavity --obfuscate -v"
    )

    # 2. Define the 3 file paths as POSITIONAL arguments (No dashes)
    # The user MUST provide them in this exact order.
    parser.add_argument("base_file", type=str, help="Path to the base file (e.g., original PDF).")
    parser.add_argument("payload_file", type=str, help="Path to the payload file (e.g., JavaScript).")
    parser.add_argument("output_file", type=str, help="Path for the resulting output file.")

    # 3. Define the boolean verbose flag (Optional, hence the dashes)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("-o", "--obfuscate", action="store_true", help="Hides the presence of the payload in the PDF structure by obfuscating the injected code.")



    # 4. Define the 'type' argument restricted to 4 options (Flag required)
    parser.add_argument(
        "-t", "--type", 
        required=True, 
        choices=["stack", "cavity", "zipper", "original"], 
        help="Injection strategy to use. Valid options: stack, cavity, zipper, original. Original won't modify the structure of the script, just can apply obfuscation if the flag -o is set"
    )



    # 5. Parse the user input
    args = parser.parse_args()

    # --- PROGRAM LOGIC STARTS HERE ---



    # Validate that input files exist
    if args.type != "original" and not os.path.exists(args.base_file):
        print(f"[-] Error: The file '{args.base_file}' does not exist.")
        sys.exit(1)
    if not os.path.exists(args.payload_file):
        print(f"[-] Error: The file '{args.payload_file}' does not exist.")
        sys.exit(1)


    if args.type != "original" and get_extension(args.base_file) != ".pdf":
        print(f"[ERROR] {args.base_file} is not a PDF file. The base file must have a .pdf extension.")
        sys.exit(1)

    if get_extension(args.payload_file) not in [".sh", ".rb", ".py", ".js"]:
        print(f"[ERROR] {args.payload_file} has unsupported extension {get_extension(args.payload_file)}. Supported extensions are .sh, .rb, .py, and .js.")
        sys.exit(1)


    # Branching based on the chosen type
    if args.verbose:
        print(f"Base file: {args.base_file}")
        print(f"Payload file: {args.payload_file}")
        print(f"Output file: {args.output_file}")


        if args.type == "stack":
            print("[*] Executing STACK algorithm...")
        
        elif args.type == "cavity":
            print("[*] Executing CAVITY algorithm...")
        
        elif args.type == "zipper":
            print("[*] Executing ZIPPER algorithm...")

        elif args.type == "original":
            if args.obfuscate:
                print("[*] Executing ORIGINAL algorithm with OBFUSCATION...")
            else:
                print("[*] Executing ORIGINAL algorithm (without obfuscation)...")

          

    if args.type == "original":
            
        with open(args.payload_file, 'rb') as payload_f:
                payload_data = payload_f.read()
        
        if args.obfuscate:
            payload_data = obfuscate_payload(payload_data, get_extension(args.payload_file))
        # if -t original and no -o, we simply copy the payload to the output file without modifying it
        with open(args.output_file, 'wb') as output_f:
            output_f.write(payload_data)  

    else:
        merge_pdf(args.base_file, args.payload_file, args.output_file, args.type, args.verbose, args.obfuscate)

    



if __name__ == "__main__":
    main()

