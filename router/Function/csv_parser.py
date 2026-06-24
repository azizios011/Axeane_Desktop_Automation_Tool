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

def parse_number(value):
    """Parse numeric values handling French format, quotes, and edge cases."""
    if value is None:
        return 0.0
    
    # If already a number, return it
    if isinstance(value, (int, float)):
        return float(value)
    
    # Convert to string and clean
    value = str(value).strip()
    
    if not value or value == '':
        return 0.0
    
    # Remove quotes (CSV sometimes includes them)
    value = value.strip('"\'')
    
    # Remove thousand separators (commas) and spaces
    value = value.replace(',', '').replace(' ', '').replace('\u00a0', '')
    
    try:
        result = float(value)
        return result
    except ValueError as e:
        log.warn(f"Could not parse number: '{value}' - {e}")
        return 0.0

def parse_percentage(value):
    """Parse percentage values like '19.00 %' -> 19.0"""
    if value is None:
        return 0.0
    
    # If already a number, return it
    if isinstance(value, (int, float)):
        return float(value)
    
    # Convert to string and clean
    value = str(value).strip()
    
    if not value or value == '':
        return 0.0
    
    # Remove quotes
    value = value.strip('"\'')
    
    # Remove percentage sign, spaces, and convert comma to dot
    value = value.replace('%', '').replace(' ', '').replace(',', '.')
    
    try:
        result = float(value)
        return result
    except ValueError as e:
        log.warn(f"Could not parse percentage: '{value}' - {e}")
        return 0.0

def parse_vente_csv(file_path: str) -> tuple:
    """Reads the Vente CSV and maps columns to the JSON structure."""
    log.info(f"Starting CSV parse for: {file_path}")
    
    # Load structure
    struct_path = "DB/Vente_Structure.json"
    if not os.path.exists(struct_path):
        log.error(f"Structure file not found: {struct_path}")
        return [], []
        
    with open(struct_path, 'r', encoding='utf-8') as f:
        structure = strip_keys(json.load(f))
        
    col_map = structure.get("column_mapping", {})
    log.debug(f"Column mapping loaded: {col_map}")
    
    data = []
    errors = 0
    csv_headers = []
    
    try:
        # Use utf-8-sig to handle BOM
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            # Detect delimiter
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
                    
                    # Parse all columns
                    parsed_row = {}
                    for csv_col in csv_headers:
                        csv_col_stripped = csv_col.strip()
                        val = row.get(csv_col_stripped, "")
                        
                        # Get internal key for type conversion
                        internal_key = col_map.get(csv_col_stripped, csv_col_stripped)
                        
                        # Type conversion based on field type
                        if internal_key in ["net_ht", "tva_amt", "ttc", "ht_brut", "remise", "net_ht_raw", "fodec"]:
                            parsed_val = parse_number(val)
                            parsed_row[csv_col_stripped] = parsed_val
                            parsed_row[internal_key] = parsed_val
                        elif internal_key == "tva_rate":
                            parsed_val = parse_percentage(val)
                            parsed_row[csv_col_stripped] = parsed_val
                            parsed_row[internal_key] = parsed_val
                        else:
                            # Keep as string, strip if it's a string
                            parsed_val = val.strip() if isinstance(val, str) else val
                            parsed_row[csv_col_stripped] = parsed_val
                            parsed_row[internal_key] = parsed_val
                            
                    data.append(parsed_row)
                    
                    # Log first few rows for debugging
                    if row_num <= 4:
                        log.debug(f"Row {row_num} parsed: Client={parsed_row.get('Client', '')}, TTC={parsed_row.get('TTC', 0)}, TVA%={parsed_row.get('TVA %', 0)}")
                    
                except Exception as e:
                    errors += 1
                    log.error(f"Row {row_num} parsing error: {e} | Data: {row}")
                    
    except Exception as e:
        log.error(f"Failed to open/read CSV file: {e}")
        return [], []
        
    log.success(f"CSV parsing complete. {len(data)} rows loaded, {errors} errors.")
    
    # Log sample data for verification
    if data:
        sample = data[0]
        log.debug(f"Sample parsed row: TTC={sample.get('ttc')}, TVA%={sample.get('tva_rate')}, TVA_Amt={sample.get('tva_amt')}")
    
    return data, csv_headers


def parse_bank_csv(file_path: str) -> tuple:
    """Reads the Bank CSV and maps columns to the JSON structure."""
    log.info(f"Starting Bank CSV parse for: {file_path}")

    struct_path = "DB/Bank_Structure.json"
    if not os.path.exists(struct_path):
        log.error(f"Structure file not found: {struct_path}")
        return [], []

    with open(struct_path, 'r', encoding='utf-8') as f:
        structure = strip_keys(json.load(f))

    col_map = structure.get("column_mapping", {})
    numeric_fields = set(structure.get("numeric_fields", []))
    log.debug(f"Bank column mapping loaded: {col_map}")

    data = []
    errors = 0
    csv_headers = []

    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            sample = f.read(2048)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = 'excel'

            reader = csv.DictReader(f, dialect=dialect)
            csv_headers = [h.strip().lstrip('\ufeff') for h in (reader.fieldnames or [])]

            log.info(f"Bank CSV headers found (in order): {csv_headers}")

            for row_num, row in enumerate(reader, start=2):
                try:
                    row = {k.strip().lstrip('\ufeff'): v for k, v in row.items()}

                    parsed_row = {}
                    for csv_col in csv_headers:
                        csv_col_stripped = csv_col.strip()
                        val = row.get(csv_col_stripped, "")
                        internal_key = col_map.get(csv_col_stripped, csv_col_stripped)

                        if internal_key in numeric_fields:
                            parsed_val = parse_number(val)
                        else:
                            parsed_val = val.strip() if isinstance(val, str) else val

                        parsed_row[csv_col_stripped] = parsed_val
                        parsed_row[internal_key] = parsed_val

                    amount = _resolve_bank_amount(parsed_row)
                    if amount == 0:
                        label = parsed_row.get("label", "")
                        ref = parsed_row.get("ref", "")
                        if not label and not ref:
                            log.debug(f"Row {row_num}: Skipping empty bank row")
                            continue

                    parsed_row["amount"] = amount
                    parsed_row["abs_amount"] = abs(amount)
                    parsed_row["flow"] = "credit" if amount > 0 else "debit"

                    if not parsed_row.get("ref"):
                        parsed_row["ref"] = f"BANK-{row_num - 1:05d}"

                    data.append(parsed_row)

                    if row_num <= 4:
                        log.debug(
                            f"Bank row {row_num} parsed: Ref={parsed_row.get('ref')}, "
                            f"Amount={parsed_row.get('amount')}, Label={parsed_row.get('label', '')[:40]}"
                        )

                except Exception as e:
                    errors += 1
                    log.error(f"Bank row {row_num} parsing error: {e} | Data: {row}")

    except Exception as e:
        log.error(f"Failed to open/read Bank CSV file: {e}")
        return [], []

    log.success(f"Bank CSV parsing complete. {len(data)} rows loaded, {errors} errors.")
    return data, csv_headers


def _resolve_bank_amount(row: dict) -> float:
    """
    Bank CSVs may provide either a signed Amount column or split Debit/Credit
    columns. Positive amounts are money in; negative amounts are money out.
    """
    signed_amount = float(row.get("amount", 0) or 0)
    if signed_amount != 0:
        return signed_amount

    debit = float(row.get("debit", 0) or 0)
    credit = float(row.get("credit", 0) or 0)

    if credit:
        return abs(credit)
    if debit:
        return -abs(debit)
    return 0.0
