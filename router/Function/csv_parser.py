# Function/csv_parser.py
import csv
import json
import os
from Debug.Logger import ColorLogger as log

def strip_keys(d):
    """Recursively strip whitespace from dictionary keys."""
    if isinstance(d, dict):
        return {k.strip(): strip_keys(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [strip_keys(i) for i in d]
    return d

def parse_vente_csv(file_path: str) -> tuple:
    """
    Reads the Vente CSV and maps columns to the JSON structure.
    Returns: (parsed_data_list, csv_headers_list)
    """
    log.info(f"Starting CSV parse for: {file_path}")
    
    # Load structure
    struct_path = "DB/Vente_Structure.json"
    if not os.path.exists(struct_path):
        log.error(f"Structure file not found: {struct_path}")
        return [], []  # Return empty tuple
        
    with open(struct_path, 'r', encoding='utf-8') as f:
        structure = strip_keys(json.load(f))
        
    col_map = structure.get("column_mapping", {})
    log.debug(f"Column mapping loaded: {col_map}")
    
    data = []
    errors = 0
    csv_headers = []
    
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            # Sniff delimiter
            sample = f.read(2048)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = 'excel'
                
            reader = csv.DictReader(f, dialect=dialect)
            csv_headers = reader.fieldnames
            
            # Strip BOM and whitespace from headers
            csv_headers = [h.strip().lstrip('\ufeff') for h in csv_headers]
            
            log.info(f"CSV Headers found (in order): {csv_headers}")
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Strip BOM from all keys
                    row = {k.strip().lstrip('\ufeff'): v for k, v in row.items()}
                    
                    # Skip Grand Total row
                    ref_val = row.get("Reference", "").strip()
                    if not ref_val or ref_val.lower() == "grand total":
                        log.debug(f"Row {row_num}: Skipping summary/empty row")
                        continue
                    
                    # Store ALL columns from CSV in their original order
                    parsed_row = {}
                    for csv_col in csv_headers:
                        csv_col_stripped = csv_col.strip()
                        val = row.get(csv_col_stripped, "").strip() if row.get(csv_col_stripped) else ""
                        
                        # Type conversion based on internal key mapping
                        internal_key = col_map.get(csv_col_stripped, csv_col_stripped)
                        
                        if internal_key in ["net_ht", "tva_amt", "ttc", "ht_brut", "remise", "net_ht_raw", "fodec"]:
                            val = float(val.replace(",", "").replace(" ", "")) if val else 0.0
                        elif internal_key == "tva_rate":
                            val = float(val.replace("%", "").replace(",", ".").strip()) if val else 0.0
                            
                        parsed_row[csv_col_stripped] = val
                        
                    data.append(parsed_row)
                except Exception as e:
                    errors += 1
                    log.error(f"Row {row_num} parsing error: {e} | Data: {row}")
                    
    except Exception as e:
        log.error(f"Failed to open/read CSV file: {e}")
        return [], []  # Return empty tuple
        
    log.success(f"CSV parsing complete. {len(data)} rows loaded, {errors} errors.")
    return data, csv_headers  # Return both data AND headers
    