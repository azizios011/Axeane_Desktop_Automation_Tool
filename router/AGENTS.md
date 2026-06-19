---

# AGENTS.md - Guide for AI Agents Working on This Codebase

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run the application
python run.py

# Build executable
python build.py

```

---

## Project Structure

### Entry Points

* **`main.py`**: Launches the Tkinter GUI.
* **`run.py`**: CLI runner that executes environmental and dependency checks before launch.
* **`build.py`**: PyInstaller packaging configuration script.

### Data Flow

```text
  CSV File 
     │
     ▼
Function/csv_parser.py ──► raw_data (list of dicts)
                             │
                             ▼
                      Modules/FormulaEngine.py ──► template_cards (grouped by client)
                                                     │
                                                     ▼
                                              UI/review_and_rules.py ──► UI display
                                                                           │
                                                                           ▼
                                                                    UI/Execution_Tab.py ──► Playwright automation
                                                                                              │
                                                                                              ▼
                                                                                      Axeane Kompta Web App

```

---

## Key Modules

### `Function/csv_parser.py`

* Parses incoming data formats while safely handling UTF-8 BOM signatures.
* Standardizes numeric fields (safely parsing commas, percentages, and locale formats).
* Returns a structured list of dictionaries featuring normalized, clean keys.

### `Modules/FormulaEngine.py`

* Aggregates raw invoices, sorting them cleanly by client profile.
* Generates the matching template formulas mapping out the structural accounting view.
* Coordinates edge cases for multi-TVA invoices containing multiple rows under a single transaction reference.

### `Logic/accounts.py`

* Resolves arbitrary client strings down to defined configuration profiles using substring matching rules (e.g., targeting `"PASSAGER"` safely isolates strings like `"C000001 | PASSAGER"`).
* Fallbacks gracefully onto the general `DEFAULT` profile configuration when specific entries fail to match.

### `Logic/Rules.py`

* References accounting behaviors defined inside localized JSON rulesets.
* Outputs the journal entry lines calculating respective balancing split debits and credits.
* Manages functional rules processing such as `timbre fiscal` and cash ledger rerouting.

### `Function/JS_Elements.py`

* Low-level Playwright interaction wrapper designed to bypass complex AngularJS 1.x architectures.
* Implements reliable injection strategies targeting complex elements like `nya-bs-select` dropdown structures and `uib-typeahead` input containers.
* Dispatches native DOM change and blur events explicitly to force core Angular digest update cycles.

---

## Common Patterns

### Adding a New Tab

1. Create your tab layout class inside `UI/new_tab.py` matching this structure:
```python
class NewTab:
    def __init__(self, parent, shared_state):
        self.parent = parent
        self.shared_state = shared_state
        self._build_ui()

    def _build_ui(self):
        # Core UI initialization logic goes here
        pass

```


2. Register the tab engine configuration inside `main.py`:
```python
from UI.new_tab import NewTab

new_tab = NewTab(tabview, shared_state)
tabview.add(new_tab.frame, text=" 🆕 New Tab ")

```



### Adding a New Client Profile

Insert a new structural entry inside `DB/Vente_Formats.json`:

```json
{
  "match": "CLIENT NAME",
  "compte_client": "411XXX",
  "use_timbre": true,
  "use_cash": false,
  "compte_caisse": "541XXX"  // Only required if use_cash is true
}

```

---

## Debugging Automation Failures

* **API Logging:** Inspect payload transactions over `Debug/logs/network/`.
* **State Captures:** Review HTML layout snips under `Debug/logs/dom/`.
* **Scope Inspection:** Run queries using `Debug/Angular_Scope.py` to target data states inside components.
* **Standard Logs:** Monitor terminal streams for explicit `[WARNING]` alerts.

---

## Testing Checklist

### 1. CSV Parsing

* [ ] UTF-8 BOM indicators are intercepted and sanitized cleanly.
* [ ] Number formats convert reliably despite regional variations (commas, percentages).
* [ ] The localized document summary/grand total row is ignored.
* [ ] Every active column correctly pairs with its defined structural mapping keys.

### 2. Formula Generation

* [ ] Target invoices sort flawlessly into categorized client profile groups.
* [ ] Multi-TVA grouped entries are processed as a single entity.
* [ ] Calculation checks confirm balanced sheets ($\text{Debit} == \text{Credit}$).
* [ ] Fiscal stamp configurations parse correctly whenever `use_timbre: true`.
* [ ] Revenue targets transfer seamlessly to designated ledgers whenever `use_cash: true`.

### 3. Browser Automation

* [ ] Platform login operations run without errors.
* [ ] Journal categorization target types map successfully.
* [ ] Accounting timeframe drop-downs pick accurate months.
* [ ] Typeahead lookup integrations update target accounts correctly.
* [ ] Split debits and credits fill across respective table rows accurately.
* [ ] Form submission actions pass data cleanly without interruption.
* [ ] Document entry sections clear and reset gracefully between transaction loops.

---

## Common Issues

> **Issue:** `"No TVA account configured for rate X%"`
> **Solution:** Register your explicit percentage rates array directly to `tax_logic.rates` inside `DB/Vente_Rules.json`.

> **Issue:** `"Formula for FC000XXX is NOT balanced"`
> **Solution:** Usually indicative of an unhandled multi-TVA document. Verify that the total TTC calculation targets the **first row index entry only**, instead of adding the cumulative amounts of every associated line item row.

> **Issue:** `"Error adding card to treeview: 'sample_client'"`
> **Solution:** Ensure that your generated card output dictionary from `FormulaEngine.build_cards()` incorporates the explicit `sample_client` context field keys.

> **Issue:** `AngularJS form elements fail to reflect data changes after a Playwright .fill() operation`
> **Solution:** Avoid utilizing raw Playwright `.fill()` mechanisms directly. Always bridge actions using handlers inside `Function/JS_Elements.py` to trigger necessary underlying UI digest cycles.

---

## Code Style

* **Type Hinting:** Maintain static type descriptions across all functions.
* **Documentation:** Ensure public interfaces expose clarifying docstrings.
* **Logging Integration:** Enforce consistent execution logging using color targets inside `Debug/Logger.py`.
* **Error Bounds:** Enclose processing phases cleanly within `try/except` guards backed by immediate logging points.
* **JSON Integrity:** Ensure loaders pass dynamic structural configurations through `_strip_keys()` prior to access.

---

## Performance Considerations

* **Automation Overhead:** Execution routines run at a steady pace of ~2-3 seconds per invoice processing cycle.
* **Batch Operations:** Managing massive data loads (e.g., 361+ invoices) demands a processing window of roughly 15-20 minutes.
* **Scalability Note:** For high-throughput configurations, consider writing direct API payload drivers to completely bypass UI rendering steps. Analyze endpoint routing profiles using `Debug/Network.py` to design an injection pipeline that can yield up to a 10x processing speed improvement.

---

## Security Notes

* Never check active environment control documents (`.env`) into source control repositories.
* Session browser cookies are kept volatile and persist transiently inside the `.gitignore` tracked `axeane_browser_profile/` working area.
* Loggers must prioritize safety by checking, filtering, and masking sensitive target data (e.g., credentials and user passwords).
