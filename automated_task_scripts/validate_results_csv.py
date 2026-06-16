import csv
import re
from pathlib import Path

def validate_csv(filepath):
    csv_file = Path(filepath)
    
    if not csv_file.exists():
        print(f"[-] Error: No se encontró el archivo {filepath}")
        return

    print(f"[*] Iniciando validación del dataset: {csv_file.name}...\n")

    # Expresiones regulares para validación
    # SHA256: 64 caracteres alfanuméricos hexadecimales
    sha256_regex = re.compile(r"^[a-fA-F0-9]{64}$")
    # Fecha ISO 8601 (ej: 2026-04-11T12:40:31Z)
    date_regex = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    # Contadores de errores
    errors = {
        "empty_core_fields": [],
        "invalid_sha256": [],
        "missing_vt_data": [],
        "missing_triage_data": [],
        "invalid_vt_stats": [],
        "invalid_triage_score": [],
        "invalid_dates": []
    }

    # Campos que se consideran el "núcleo" y jamás deberían estar vacíos
    core_fields = ["name", "file type", "polyglot type", "sha256"]
    
    # Estadísticas de VT que deben ser números enteros si existen
    vt_stats_fields = [
        "vt_malicious", "vt_suspicious", "vt_undetected", "vt_harmless",
        "vt_timeout", "vt_confirmed_timeout", "vt_failure", "vt_type_unsupported"
    ]

    total_rows = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for line_num, row in enumerate(reader, start=2): # start=2 porque la línea 1 es la cabecera
            total_rows += 1
            row_id = row.get('sha256', f"Fila {line_num}")

            # 1. Validar campos core vacíos
            for field in core_fields:
                if not row.get(field) or str(row.get(field)).strip() == "":
                    errors["empty_core_fields"].append(f"Fila {line_num}: Falta '{field}'")

            # 2. Validar formato SHA256
            sha256_val = row.get("sha256", "").strip()
            if sha256_val and not sha256_regex.match(sha256_val):
                errors["invalid_sha256"].append(f"Fila {line_num}: SHA256 malformado ({sha256_val[:10]}...)")

            # 3. Validar datos de VirusTotal
            if not row.get("vt_date"):
                errors["missing_vt_data"].append(f"Fila {line_num} ({row_id}): Sin resultados de VT")
            else:
                # Validar fecha VT
                if not date_regex.match(row.get("vt_date", "")):
                    errors["invalid_dates"].append(f"Fila {line_num}: Fecha VT inválida ({row.get('vt_date')})")
                
                # Validar que las stats sean numéricas
                for stat in vt_stats_fields:
                    val = row.get(stat, "")
                    if val != "" and not str(val).isdigit():
                        errors["invalid_vt_stats"].append(f"Fila {line_num}: VT '{stat}' no es un entero ({val})")

            # 4. Validar datos de Triage
            if not row.get("triage_date"):
                errors["missing_triage_data"].append(f"Fila {line_num} ({row_id}): Sin resultados de Triage")
            else:
                # Validar fecha Triage
                if not date_regex.match(row.get("triage_date", "")):
                    errors["invalid_dates"].append(f"Fila {line_num}: Fecha Triage inválida ({row.get('triage_date')})")
                
                # Validar que el score sea un número entre 0 y 10
                score_val = row.get("triage_score", "")
                if score_val != "":
                    try:
                        score_int = int(score_val)
                        if score_int < 0 or score_int > 10:
                            errors["invalid_triage_score"].append(f"Fila {line_num}: Score fuera de rango 0-10 ({score_val})")
                    except ValueError:
                        errors["invalid_triage_score"].append(f"Fila {line_num}: Triage score no es numérico ({score_val})")

            # check virus total number of engines is consistent with malicious + suspicious + undetected + harmless
            if row.get("vt_date") and all(row.get(stat, "") != "" for stat in vt_stats_fields):
                try:
                    total_engines = sum(int(row.get(stat, "0")) for stat in vt_stats_fields if stat != "vt_date")
                    if total_engines!= 76:
                        print (row, total_engines)
                #     if total_engines != int(row.get("vt_malicious", "0")) + int(row.get("vt_suspicious", "0")) + int(row.get("vt_undetected", "0")) + int(row.get("vt_harmless", "0")):
                #         errors["invalid_vt_stats"].append(f"Fila {line_num}: Total de motores no coincide con suma de categorías ({total_engines} vs {row.get('vt_malicious', '0')}+{row.get('vt_suspicious', '0')}+{row.get('vt_undetected', '0')}+{row.get('vt_harmless', '0')})")
                except ValueError:
                    # Si alguna de las stats no es numérica, ya se reportó en invalid_vt_stats, así que lo ignoramos aquí
                    pass

    # ==========================================
    # IMPRESIÓN DEL REPORTE
    # ==========================================
    print(f"--- REPORTE DE VALIDACIÓN ---")
    print(f"Total de filas analizadas: {total_rows}\n")

    total_errors = sum(len(lst) for lst in errors.values())
    
    if total_errors == 0:
        print("[+] ¡Enhorabuena! El dataset está impoluto. Todos los campos y formatos son correctos.")
    else:
        print(f"[!] Se encontraron {total_errors} incidencias en el dataset:\n")
        
        error_titles = {
            "empty_core_fields": "Campos principales vacíos (Crítico):",
            "invalid_sha256": "Hashes SHA256 malformados:",
            "missing_vt_data": "Faltan datos de VirusTotal (Muestra no analizada o fallida):",
            "missing_triage_data": "Faltan datos de Triage (Muestra no analizada o fallida):",
            "invalid_vt_stats": "Estadísticas de VT con formato incorrecto (No numérico):",
            "invalid_triage_score": "Score de Triage con formato incorrecto (No numérico o fuera de rango):",
            "invalid_dates": "Fechas con formato incorrecto (Esperado: ISO 8601):"
        }

        for key, title in error_titles.items():
            if errors[key]:
                print(f"[*] {title} ({len(errors[key])})")
                # Mostrar solo los primeros 10 para no saturar la consola si hay cientos
                for msg in errors[key][:10]:
                    print(f"    - {msg}")
                if len(errors[key]) > 10:
                    print(f"    ... y {len(errors[key]) - 10} más.")
                print("")

if __name__ == "__main__":
    # Asegúrate de poner la ruta correcta a tu results.csv
    validate_csv("../results.csv")