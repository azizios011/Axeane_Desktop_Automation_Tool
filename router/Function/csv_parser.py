# Function/csv_parser.py
import csv
import json
import os
from Debug.Logger import ColorLogger as log

def strip_keys(d):
    """Recursively strip whitespace from dictionary keys to fix JSON formatting issues."""
    if isinstance(d, dict):
        return {k.strip(): strip_keys(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [strip_keys(i) for i in d]
    return d

def parse_vente_csv(file_path: str) -> list:
    """Reads the Vente CSV and maps columns to the JSON structure."""
    log.info(f"Starting CSV parse for: {file_path}")
    
    # Load structure
    struct_path = "DB/Vente_Structure.json"
    if not os.path.exists(struct_path):
        log.error(f"Structure file not found: {struct_path}")
        return []
        
    with open(struct_path, 'r', encoding='utf-8') as f:
        structure = strip_keys(json.load(f))
        
    col_map = structure.get("column_mapping", {})
    log.debug(f"Column mapping loaded: {col_map}")
    
    data = []
    errors = 0
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            # Sniff delimiter just in case, but default to comma
            sample = f.read(2048)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = 'excel'
                
            reader = csv.DictReader(f, dialect=dialect)
            csv_headers = reader.fieldnames
            log.info(f"CSV Headers found: {csv_headers}")
            
            for row_num, row in enumerate(reader, start=2): # start=2 because row 1 is header
                try:
                    parsed_row = {}
                    for csv_col, internal_key in col_map.items():
                        internal_key = internal_key.strip()
                        csv_col = csv_col.strip()
                        
                        if csv_col not in row:
                            log.warn(f"Row {row_num}: Missing column '{csv_col}' in CSV")
                            continue
                            
                        val = row[csv_col].strip() if row[csv_col] else ""
                        
                        # Type conversion based on internal key
                        if internal_key in ["net_ht", "tva_amt", "ttc"]:
                            # Handle thousand separators (commas) and decimal points
                            val = float(val.replace(",", "").replace(" ", "")) if val else 0.0
                        elif internal_key == "tva_rate":
                            # Handle "19.00 %" -> 19.00
                            val = float(val.replace("%", "").replace(",", ".").strip()) if val else 0.0
                            
                        parsed_row[internal_key] = val
                        
                    data.append(parsed_row)
                except Exception as e:
                    errors += 1
                    log.error(f"Row {row_num} parsing error: {e} | Data: {row}")
                    
    except Exception as e:
        log.error(f"Failed to open/read CSV file: {e}")
        return []
        
    log.success(f"CSV parsing complete. {len(data)} rows loaded, {errors} errors.")
    return data
    