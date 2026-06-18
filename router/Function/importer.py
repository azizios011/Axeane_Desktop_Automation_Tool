# Function/import.py
from .csv_parser import parse_vente_csv
from Logic.Rules import VenteRulesEngine

def import_and_process_vente(file_path: str):
    raw_data = parse_vente_csv(file_path)
    engine = VenteRulesEngine()
    processed_entries = []
    
    for row in raw_data:
        # Apply rules from DB/Vente_Rules.json
        journal_entry = engine.process_sale(row)
        processed_entries.append(journal_entry)
        
    return processed_entries
    