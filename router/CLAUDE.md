---

# CLAUDE.md - Project Context for Claude AI

## Project Overview

**Axeane Kompta Desktop Automation Tool** is a Python desktop application that automates accounting entry creation in the Axeane Kompta web application. It reads CSV files of sales invoices, applies configurable accounting rules, and automatically populates web forms using Playwright browser automation.

---

## Core Architecture

```text
Axeane_Desktop_Automation_Tool/
├── main.py                    # Entry point - launches Tkinter UI
├── run.py                     # CLI runner with dependency checks
├── build.py                   # PyInstaller build system
├── Function/                  # Core business logic
│   ├── csv_parser.py          # CSV parsing with BOM handling
│   └── JS_Elements.py         # Playwright interactions with AngularJS
├── Moduls/                    # Browser/session management
│   ├── Session.py             # Browser session lifecycle
│   ├── CDP_Setting.py         # Chrome DevTools Protocol config
│   └── FormulaEngine.py       # Groups invoices by client profile
├── Logic/                     # Business rules
│   ├── accounts.py            # Client profile matching
│   └── Rules.py               # Accounting rules engine
├── Models/                    # UI components for Axeane web app
│   ├── EcritureHeader.py
│   ├── EcritureTable.py
│   └── EcritureActions.py
├── UI/                        # Tkinter desktop UI
│   ├── App.py
│   ├── Settings_Tab.py
│   ├── PWA_Tab.py
│   ├── Import_Tab.py
│   ├── review_and_rules.py    # Template cards view
│   └── Execution_Tab.py
├── Debug/                     # Debugging tools
│   ├── Network.py             # API request/response logging
│   ├── Angular_Scope.py       # AngularJS scope inspection
│   ├── DOM_Inspector.py       # HTML snapshots
│   └── Logger.py              # Color-coded console logger
└── DB/                        # Configuration JSON files
    ├── Vente_Formats.json     # Client profiles
    ├── Bank_Formats.json      # Bank transaction keywords
    ├── Vente_Rules.json       # Sales accounting rules
    ├── Bank_Rules.json        # Bank accounting rules
    ├── Vente_Structure.json   # CSV column mapping (sales)
    └── Bank_Structure.json    # CSV column mapping (bank)

```

---

## Critical Gotchas

### 1. JSON Trailing Spaces

JSON configuration files in `DB/` often contain trailing spaces in keys (e.g., `"match "` instead of `"match"`). **All JSON loaders must use `_strip_keys()` to normalize data:**

```python
def _strip_keys(self, d):
    if isinstance(d, dict):
        return {k.strip(): self._strip_keys(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [self._strip_keys(i) for i in d]
    return d

```

### 2. CSV BOM Handling

CSV files exported from Microsoft Excel often include a UTF-8 BOM character. Always use `encoding='utf-8-sig'` when reading input files:

```python
with open(file_path, mode='r', encoding='utf-8-sig') as f:
    # Processing logic

```

### 3. Multi-TVA Invoices

Some invoices split amounts across multiple TVA rates (e.g., 7% + 19%). In the raw CSV data, these appear as multiple rows sharing an identical invoice Reference. **You must group rows by reference prior to processing:**

```python
from collections import defaultdict

ref_groups = defaultdict(list)
for row in rows:
    ref = row.get("ref", "UNKNOWN")
    ref_groups[ref].append(row)

```

### 4. AngularJS Interactions

The Axeane web application runs on AngularJS 1.x utilizing custom directives. Standard Playwright `.fill()` methods typically fail to trigger the Angular digest cycle.

> **Rule:** Always use the custom interaction methods defined in `Function/JS_Elements.py` that explicitly dispatch `blur` and `change` events to force data binding updates.

### 5. Client Profile Matching

Clients are resolved via a substring match on the full client string (e.g., parsing `"C000001 | PASSAGER"`). Order of execution is critical here: check specific client profiles first before falling back to the `DEFAULT` profile.

---

## Key Business Logic

### Invoice Grouping

Invoices are aggregated and processed by client profiles rather than individually:

* **PASSAGER:** Cash clients with timbre (148 invoices in test data).
* **TUNISIE AUTOMOTIVE:** Specific client account `411032`.
* **STE OTO MOOVE:** Specific client account `411053`.
* **DEFAULT:** Fallback group for all remaining clients (216 invoices in test data).

### Formula Generation & Validation

The UI dynamically renders profile template cards containing:

* Profile name and matching type rule.
* Total invoice count within the group.
* Total cumulative TTC amount.
* Generated accounting formula layout (Account, Label, Debit, Credit).
* A visual balancing validation status ($✓$ or $✗$).

### Balance Calculation (Multi-TVA)

For multi-TVA invoice groups, balancing must be strictly verified before running automation:

* **Debit:** Total TTC (Extracted from the **first row only**—all related rows share the same total TTC).
* **Credit:** Calculated as $\sum(\text{TVA amounts} + \text{HT amounts} + \text{Timbre})$.
* **Condition:** Must balance exactly: $\text{Debit} == \text{Credit}$.

---

## Testing Approach

* **Test Dataset:** `data/journal vte mars 26(Sheet1)(1).csv`
* **Row Validation:** Verify that exactly 366 rows are parsed (representing 366 total rows including 1 grand total row).
* **Reference Validation:** Verify exactly 361 unique references (accounting for the 5 multi-TVA invoices containing 2 rows each).
* **UI Validation:** Confirm 4 distinct template cards are generated in the tab view and ensure all cards evaluate to a $✓$ balanced status.

---

## Common Workflows

### Adding a New Client Profile

Append the new routing rule to `DB/Vente_Formats.json`:

```json
{
  "match": "NEW CLIENT NAME",
  "compte_client": "411XXX",
  "use_timbre": true,
  "use_cash": false
}

```

### Adding a New TVA Rate

Register the mapping rules inside `DB/Vente_Rules.json`:

```json
{
  "rate": 13,
  "ht_account": "707013",
  "tva_account": "436713"
}

```

### Debugging Browser Automation

* Activate `Debug/Network.py` to capture and stream backend API payloads.
* Use `Debug/Angular_Scope.py` to live-inspect active target elements scopes.
* Utilize `Debug/DOM_Inspector.py` to extract quick HTML state snapshots.

---

## Performance Notes

* **Execution Speed:** Browser automation currently processes at approximately ~2-3 seconds per invoice.
* **Total Runtime:** Processing 361 invoices takes roughly 15-20 minutes.
* *Optimization Note:* If production speeds require optimization, consider migrating away from UI automation toward an API-driven entry injector (refer to network patterns logged by `Debug/Network.py`).
