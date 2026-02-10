#!/bin/bash

POC_DIR="../PoC"

echo "[*] Creating malware-style ZIPs for each PoC folder..."

for folder in "$POC_DIR"/*/; do
    [ -d "$folder" ] || continue

    dirname=$(basename "$folder")
    zip_path="${folder}${dirname}.zip"

    echo "[+] Processing: $dirname"

    # Encontrar scripts y PDF, ignorando TXT
    files_to_zip=$(find "$folder" -maxdepth 1 -type f \
        \( -name "*.pdf" -o -name "*.rb" -o -name "*.py" -o -name "*.sh" \))

    if [ -z "$files_to_zip" ]; then
        echo "  - No PDF/Ruby/Python/Bash files found. Skipping."
        continue
    fi

    echo "  - Creating ZIP with password 'infected'..."

    zip -j -P "infected" "$zip_path" $files_to_zip > /dev/null

    echo "  - ZIP created: $zip_path"

    echo "  - Removing original files..."
    rm -f $files_to_zip

    echo "  - Done."
done

echo "[+] Task completed."
