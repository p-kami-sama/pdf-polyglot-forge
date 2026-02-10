#!/usr/bin/env bash

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POC_DIR="$BASE_DIR/PoC"

echo "[*] Checking polyglot script syntax under $POC_DIR"
echo

for DIR in "$POC_DIR"/*; do
    [[ -d "$DIR" ]] || continue

    DIR_NAME="$(basename "$DIR")"

    # Detect type
    if [[ "$DIR_NAME" == *_bash.sh ]]; then
        SCRIPT_TYPE="bash"
    elif [[ "$DIR_NAME" == *_python.py ]]; then
        SCRIPT_TYPE="python"
    elif [[ "$DIR_NAME" == *_ruby.rb ]]; then
        SCRIPT_TYPE="ruby"
    else
        continue
    fi

    echo "[*] Processing directory: $DIR_NAME ($SCRIPT_TYPE)"

    RESULTS_FILE="$DIR/results.txt"

    # Process all PDFs (polyglots)
    for PDF in "$DIR"/*.pdf; do
        [[ -f "$PDF" ]] || continue

        PDF_NAME="$(basename "$PDF")"
        printf "  - %-25s : " "$PDF_NAME"

        if [[ "$SCRIPT_TYPE" == "bash" ]]; then
            # Extract Bash part until the first "exit" on its own line
            TMP_SCRIPT=$(mktemp)

            awk '
                BEGIN { inside=1 }
                /^[[:space:]]*exit[[:space:]]*$/ { inside=0 }
                inside == 1 { print }
            ' "$PDF" > "$TMP_SCRIPT"

            if bash -n "$TMP_SCRIPT" 2>/dev/null; then
                echo "OK"
            else
                echo "ERROR"
            fi

            rm -f "$TMP_SCRIPT"

        elif [[ "$SCRIPT_TYPE" == "python" ]]; then
            if python3 -m py_compile "$PDF" 2>/dev/null; then
                echo "OK"
            else
                echo "ERROR"
            fi

        elif [[ "$SCRIPT_TYPE" == "ruby" ]]; then
	    if ruby -c "$PDF" >/dev/null 2>&1; then
                echo "OK"
            else
                echo "ERROR"
            fi
#                ;;
        fi
    done

    echo
done

echo "[+] Syntax verification completed."



