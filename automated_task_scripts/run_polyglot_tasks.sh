#!/usr/bin/env bash

set -euo pipefail

# Directorios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
POC_DIR="$BASE_DIR/PoC"

PDF_NAME="sample.pdf"
POLYGLOT_SCRIPT="$BASE_DIR/make_pdf_polyglot.py"

# Lista de scripts keep
KEEP_FILES=()
for f in "$BASE_DIR"/*; do
    [[ -f "$f" ]] || continue
    case "$(basename "$f")" in
        "$PDF_NAME" | "make_pdf_polyglot.py")
            ;;
        *)
            KEEP_FILES+=("$(basename "$f")")
            ;;
    esac
done

echo "[*] Preparing PoC directory structure..."

mkdir -p "$POC_DIR"

if [[ -f "$BASE_DIR/$PDF_NAME" ]]; then
    mv "$BASE_DIR/$PDF_NAME" "$POC_DIR/"
fi

for keep in "${KEEP_FILES[@]}"; do
    KEEP_NAME="$(basename "$keep")"
    KEEP_BASE="${KEEP_NAME%.*}"

    KEEP_DIR="$POC_DIR/$KEEP_NAME"
    mkdir -p "$KEEP_DIR"

    if [[ -f "$BASE_DIR/$KEEP_NAME" ]]; then
        mv "$BASE_DIR/$KEEP_NAME" "$KEEP_DIR/"
    fi

    echo "[*] Processing $KEEP_NAME..."

    pushd "$KEEP_DIR" > /dev/null

    # ================================
    # 🆕 inicializar ficheros
    # ================================
    COMMANDS_FILE="commands.txt"
    RESULTS_FILE="results.txt"

    : > "$COMMANDS_FILE"     # limpiar/crear
: > "$RESULTS_FILE"
cat << 'EOF' > "$RESULTS_FILE"
SOURCE OF THE MALWARE:


CLEAR FILE:



START:


END:
EOF

    # ================================
    # 🆕 definir comandos
    # ================================
    CMD_START=(python3 "$POLYGLOT_SCRIPT" --input "../$PDF_NAME" --keep "$KEEP_NAME" --output "${KEEP_BASE}_start.pdf" --start)
    CMD_MIDDLE=(python3 "$POLYGLOT_SCRIPT" --input "../$PDF_NAME" --keep "$KEEP_NAME" --output "${KEEP_BASE}_middle.pdf" --middle)
    CMD_END=(python3 "$POLYGLOT_SCRIPT" --input "../$PDF_NAME" --keep "$KEEP_NAME" --output "${KEEP_BASE}_end.pdf")

    # ================================
    # ▶️ Ejecución real
    # ================================
    "${CMD_START[@]}"
    "${CMD_MIDDLE[@]}"
    "${CMD_END[@]}"
    
    
    # ================================
    # 🆕 definir comandos relativos
    # ================================
    CMD_START=(python3 "../make_pdf_polyglot.py" --input "../$PDF_NAME" --keep "$KEEP_NAME" --output "${KEEP_BASE}_start.pdf" --start)
    CMD_MIDDLE=(python3 "../make_pdf_polyglot.py" --input "../$PDF_NAME" --keep "$KEEP_NAME" --output "${KEEP_BASE}_middle.pdf" --middle)
    CMD_END=(python3 "../make_pdf_polyglot.py" --input "../$PDF_NAME" --keep "$KEEP_NAME" --output "${KEEP_BASE}_end.pdf")

    # ================================
    # 🆕 guardar comandos
    # ================================
    printf "%q " "${CMD_START[@]}"  >> "$COMMANDS_FILE"; echo >> "$COMMANDS_FILE"
    printf "%q " "${CMD_MIDDLE[@]}" >> "$COMMANDS_FILE"; echo >> "$COMMANDS_FILE"
    printf "%q " "${CMD_END[@]}"    >> "$COMMANDS_FILE"; echo >> "$COMMANDS_FILE"


    popd > /dev/null
done

echo "[+] All polyglot PDFs generated successfully."
