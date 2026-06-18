# Function/csv_parser.py
import csv
import json

def parse_vente_csv(file_path: str) -> list:
    """Reads the Vente CSV and maps columns to the JSON structure."""
    data = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Map CSV headers to your Vente_Structure.json keys
            data.append({
                "ref": row.get("Reference"),
                "date": row.get("Date"),
                "client_name": row.get("Client"),
                "net_ht": float(row.get("Tot. Net. HT", 0)),
                "tva_rate": int(row.get("TVA %", 0)),
                "tva_amt": float(row.get("Montant TVA", 0)),
                "ttc": float(row.get("TTC", 0))
            })
    return data
