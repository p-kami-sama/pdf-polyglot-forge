import os
import random
import string
import re

import argparse
import sys

def merge_pdf_mp3(pdf_file, mp3_file, output_file, verbose, append_at_the_beginning = False):
    if append_at_the_beginning:
        if os.path.getsize(mp3_file) > 1000:
            # print("The audio file is too large to be appended at the beginning, it will be appended at the end. Files larger than 1000 bytes cannot be appended at the beginning.")
            # append_at_the_beginning = False
            pass
        elif verbose:
            print("Appending audio file at the beginning...")
    if verbose and not append_at_the_beginning:
        print("Appending audio file at the end...")

    with open(pdf_file, 'rb') as pdf_f:  # Abrimos el archivo PDF
        pdf_data = pdf_f.read()
    
    with open(mp3_file, 'rb') as mp3_f: # Abrimos el archivo MP3
        hide_data = mp3_f.read()
    
    with open(output_file, 'wb') as output_f:   # Creamos el archivo de salida en modo binario
        if append_at_the_beginning:
            output_f.write(hide_data)
            output_f.write(pdf_data)
        else:
            output_f.write(pdf_data)
            output_f.write(hide_data)






def merge_pdf_sh(pdf_file, sh_file, output_file, verbose, append_at_the_beginning = False):
    if append_at_the_beginning:
        if os.path.getsize(sh_file) > 1000:
            # print("The sh file is too large to be appended at the beginning, it will be appended at the end. Files larger than 1000 bytes cannot be appended at the beginning.")
            # append_at_the_beginning = False
            pass
        elif verbose:
            print("Appending sh file at the beginning...")
    if verbose and not append_at_the_beginning:
        print("Appending sh file at the end...")


    with open(pdf_file, 'rb') as pdf_f:
        pdf_data = pdf_f.read()
    
    with open(sh_file, 'rb') as sh_f:
        hide_data = sh_f.read()
    
    with open(output_file, 'wb') as output_f:   # Creamos el archivo de salida en modo binario

        if append_at_the_beginning:
            output_f.write(hide_data)  # Escribir el script shell como bytes
            output_f.write(b"\nexit\n")  # Asegurarse de que haya una nueva línea después de %%EOF
            output_f.write(pdf_data)
        else:
            random_comment_word = ''.join(random.choices(string.ascii_letters, k=random.randint(8, 12)))
            output_f.write(f": << '{random_comment_word}'\n".encode())
            output_f.write(pdf_data)
            output_f.write(f"\n{random_comment_word}\n".encode())
            output_f.write(hide_data)  # Escribir el script shell como bytes
            output_f.write(b"\nexit\n")  # Asegurarse de que haya una nueva línea después de %%EOF

                    



def merge_pdf_ruby(pdf_file, ruby_file, output_file, verbose, append_at_the_beginning = False):
    if append_at_the_beginning:
        if os.path.getsize(ruby_file) > 1000:
            # print("The ruby file is too large to be appended at the beginning, it will be appended at the end. Files larger than 1000 bytes cannot be appended at the beginning.")
            # append_at_the_beginning = False
            pass
        elif verbose:
            print("Appending ruby file at the beginning...")
    if verbose and not append_at_the_beginning:
        print("Appending ruby file at the end...")

    with open(pdf_file, 'rb') as pdf_f:
        pdf_data = pdf_f.read()
    
    with open(ruby_file, 'rb') as mp3_f:
        hide_data = mp3_f.read()
    
    with open(output_file, 'wb') as output_f:
        if append_at_the_beginning:
            output_f.write(hide_data)
            output_f.write("\n=begin\n".encode())
            output_f.write(pdf_data)
            output_f.write("\n=end\n".encode())
        else:
        
            shebang = b""
            encoding_line = b""
            rest_of_script = hide_data

            # Dividir por líneas solo para analizar encabezados
            lines = hide_data.split(b"\n")

            idx = 0

            # 1) SHEBANG
            if lines and lines[0].startswith(b"#!"):
                shebang = lines[0] + b"\n"
                idx = 1

            # 2) ENCODING (Ruby reconoce varias formas)
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

            # El resto del script tras shebang + encoding
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


def merge_pdf_py(pdf_file, python_file, output_file, verbose, append_at_the_beginning = False):
    if append_at_the_beginning:
        if os.path.getsize(python_file) > 1000:
            # print("The python file is too large to be appended at the beginning, it will be appended at the end. Files larger than 1000 bytes cannot be appended at the beginning.")
            # append_at_the_beginning = False
            pass
        elif verbose:
            print("Appending python file at the beginning...")
    if verbose and not append_at_the_beginning:
        print("Appending python file at the end...")

    with open(pdf_file, 'rb') as pdf_f:
        pdf_data = pdf_f.read()
        print(type(pdf_data))
    
        if b'\x00' in pdf_data:
            print("The PDF file has a null byte, so the Python code probably doesn't work. Please try another PDF.")
        elif verbose:
            print("No null byte found in the PDF file, continuing with the process.")
    
    with open(python_file, 'rb') as hide_f:
        hide_data = hide_f.read()
    
    encoding = '''# coding: iso-8859-1 -*-'''

    with open(output_file, 'wb') as output_f:
        if append_at_the_beginning:
            output_f.write(encoding.encode("iso-8859-1"))
            output_f.write(b'\n')

            output_f.write(hide_data)
            output_f.write(b'\nr"""\n')
            output_f.write(pdf_data)
            output_f.write(b'"""\n')
        else:
            output_f.write(encoding.encode("iso-8859-1"))
            output_f.write(b'\nr"""\n')
            output_f.write(pdf_data)
            output_f.write(b'"""\n')
            output_f.write(hide_data)



def merge_pdf_sh_middle(pdf_file, sh_file, output_file, verbose: bool = False):

    with open(pdf_file, 'rb') as pdf_f:
        if verbose:
            print("Reading PDF file...")
        pdf_data = pdf_f.read()
    
    with open(sh_file, 'rb') as sh_f:
        if verbose:
            print("Reading shell script file...")
        hide_data = sh_f.read()


    # Buscar un punto adecuado entre los objetos del PDF
    # Patrón común que indica final de un objeto: "endobj" seguido de una nueva línea
    matches = list(re.finditer(rb'\nendobj[\r]?\n', pdf_data))
    if not matches:
        raise ValueError("PDF objects to insert the script not found. Ensure the PDF is valid and contains objects.")

    # Punto intermedio entre objetos para la inserción
    insert_pos = matches[len(matches) // 2].end()

    # Dividir el PDF en dos partes:
    pdf_part1 = pdf_data[:insert_pos]
    pdf_part2 = pdf_data[insert_pos:]

    # Generar una palabra aleatoria para usarse como comentario de Bash
    random_comment_word = ''.join(random.choices(string.ascii_letters, k=random.randint(8, 12)))

    if verbose:
        print(f"Inserting shell script at position {insert_pos} in the PDF file.")
    
    # Payload Bash: se encierra la primera parte del PDF en un comentario multilinea
    bash_payload = f": << '{random_comment_word}'\n".encode("utf-8")
    bash_payload += pdf_part1
    bash_payload += f"\n{random_comment_word}\n".encode("utf-8")

    bash_payload += hide_data  # Agregar el script Bash como bytes
    bash_payload += "\nexit\n".encode("utf-8")  # Finalizar el script Bash
    
    # Ensamblar el PDF final con Bash embebido
    with open(output_file, "wb") as f:
        f.write(bash_payload)
        f.write(pdf_part2)



def merge_pdf_ruby_middle(pdf_file, ruby_file, output_file, verbose: bool = False):

    with open(pdf_file, 'rb') as pdf_f:
        if verbose:
            print("Reading PDF file...")
        pdf_data = pdf_f.read()
    
    with open(ruby_file, 'rb') as rb_f:
        if verbose:
            print("Reading ruby script file...")
        hide_data = rb_f.read()


    shebang = b""
    encoding_line = b""
    rest_of_script = hide_data


    # Dividir por líneas solo para analizar encabezados
    lines = hide_data.split(b"\n")

    idx = 0

    # 1) SHEBANG
    if lines and lines[0].startswith(b"#!"):
        shebang = lines[0] + b"\n"
        idx = 1

    # 2) ENCODING (Ruby reconoce varias formas)
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

    # El resto del script tras shebang + encoding
    rest_of_script = b"\n".join(lines[idx:]) + b"\n"




    # Buscar un punto adecuado entre objetos del PDF
    matches = list(re.finditer(rb'\nendobj[\r]?\n', pdf_data))
    if not matches:
        raise ValueError(
            "PDF objects to insert the script not found. Ensure the PDF is valid and contains objects."
        )

    # Punto intermedio entre objetos
    insert_pos = matches[len(matches) // 2].end()

    # Dividir el PDF
    pdf_part1 = pdf_data[:insert_pos]
    pdf_part2 = pdf_data[insert_pos:]

    if verbose:
        print(f"Inserting ruby script at position {insert_pos} in the PDF file.")

    # Payload Ruby:
    ruby_payload = b""

    # Prepend shebang + encoding si existen
    ruby_payload += shebang
    ruby_payload += encoding_line
    
    # Se encierra la primera parte del PDF en un comentario multilinea Ruby
    ruby_payload += b"=begin\n"
    ruby_payload += pdf_part1
    ruby_payload += b"\n=end\n"

    # Agregar el script Ruby real
    ruby_payload += rest_of_script
    ruby_payload += b"\n"

    # Agregar la segunda parte del PDF también en un comentario multilinea Ruby
    ruby_payload  += b"\n=begin\n"
    ruby_payload += pdf_part2
    ruby_payload += b"\n=end\n"

    # Ensamblar PDF final
    with open(output_file, "wb") as f:
        f.write(ruby_payload)



def merge_pdf_py_middle(pdf_file, python_file, output_file, verbose: bool = False):

    with open(pdf_file, 'rb') as pdf_f:
        if verbose:
            print("Reading PDF file...")
        pdf_data = pdf_f.read()

        if b'\x00' in pdf_data:
            print(
                "The PDF file has a null byte, so the Python code probably won't work. "
                "Please try another PDF."
            )

    with open(python_file, 'r', encoding="iso-8859-1") as py_f:
        if verbose:
            print("Reading python script file...")
        hide_data = py_f.read()

    # Buscar un punto adecuado entre objetos del PDF
    matches = list(re.finditer(rb'\nendobj[\r]?\n', pdf_data))
    if not matches:
        raise ValueError(
            "PDF objects to insert the script not found. Ensure the PDF is valid and contains objects."
        )

    # Punto intermedio
    insert_pos = matches[len(matches) // 2].end()

    pdf_part1 = pdf_data[:insert_pos]
    pdf_part2 = pdf_data[insert_pos:]

    if verbose:
        print(f"Inserting python script at position {insert_pos} in the PDF file.")

    # Encoding obligatorio para Python
    encoding = "# coding: iso-8859-1 -*-\n"

    # Payload Python:
    # El PDF queda completamente encapsulado dentro de un string raw
    python_payload  = encoding.encode("iso-8859-1")
    python_payload += b"r\"\"\"\n"
    python_payload += pdf_part1
    python_payload += b"\n\"\"\"\n"

    # Código Python real
    python_payload += hide_data.encode("iso-8859-1")
    python_payload += b"\n"

    python_payload += b"\nr\"\"\"\n"
    python_payload += pdf_part2
    python_payload += b"\n\"\"\"\n"

    # Resto del PDF
    with open(output_file, "wb") as f:
        f.write(python_payload)





def get_extension(path: str) -> str:
    return os.path.splitext(path)[1].lower()

# -------------------------------------------------
# Main
# -------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Polyglot PDF merger"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="PDF de entrada"
    )

    parser.add_argument(
        "--keep",
        required=True,
        help="Archivo a incrustar (sh, py, rb, mp3)"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Archivo PDF de salida"
    )

    parser.add_argument(
        "--start",
        action="store_true",
        help="Inserta el payload al inicio del PDF"
    )

    parser.add_argument(
        "--middle",
        action="store_true",
        help="Inserta el payload en el medio del PDF"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Salida detallada"
    )

    args = parser.parse_args()

    # -------------------------------------------------
    # Validaciones básicas
    # -------------------------------------------------
    if args.start and args.middle:
        print("[ERROR] --start y --middle no pueden usarse juntos")
        sys.exit(1)

    pdf_file = args.input
    keep_file = args.keep
    output_file = args.output
    verbose = args.verbose

    ext = get_extension(keep_file)

    append_at_the_beginning = args.start

    # -------------------------------------------------
    # Dispatch por extensión y posición
    # -------------------------------------------------
    if args.middle:
        if ext == ".sh":
            merge_pdf_sh_middle(pdf_file, keep_file, output_file, verbose)
        elif ext == ".rb":
            merge_pdf_ruby_middle(pdf_file, keep_file, output_file, verbose)
        elif ext == ".py":
            merge_pdf_py_middle(pdf_file, keep_file, output_file, verbose)
        else:
            print(f"[ERROR] Modo --middle no soportado para {ext}")
            sys.exit(1)

    else:
        if ext == ".mp3":
            merge_pdf_mp3(
                pdf_file,
                keep_file,
                output_file,
                verbose,
                append_at_the_beginning
            )

        elif ext == ".sh":
            merge_pdf_sh(
                pdf_file,
                keep_file,
                output_file,
                verbose,
                append_at_the_beginning
            )

        elif ext == ".rb":
            merge_pdf_ruby(
                pdf_file,
                keep_file,
                output_file,
                verbose,
                append_at_the_beginning
            )

        elif ext == ".py":
            merge_pdf_py(
                pdf_file,
                keep_file,
                output_file,
                verbose,
                append_at_the_beginning
            )

        else:
            print(f"[ERROR] Tipo de archivo no soportado: {ext}")
            sys.exit(1)

    if verbose:
        print("[INFO] Operación completada correctamente")

# -------------------------------------------------
# Entry point
# -------------------------------------------------
if __name__ == "__main__":
    main()
