---

# Axeane Kompta Desktop Automation Tool


A Python desktop application that automates accounting entry creation in the Axeane Kompta web application. It reads CSV files of sales invoices, applies configurable accounting rules, and automatically populates web forms using Playwright browser automation.

---

## Accounting Desktop Automation Tool

## Features

* 📊 **CSV Import**: Import sales invoices from CSV files with resilient, automated structural parsing.
* 🧮 **Smart Grouping**: Automatically buckets invoices by client routing profile (`PASSAGER`, `DEFAULT`, and custom client accounts).
* 📋 **Template Preview**: Visual interface rendering preview templates of accounting formulas prior to browser routing.
* 🤖 **Browser Automation**: Fully autonomous web form entry engine built over Playwright.
* 🔄 **Multi-TVA Support**: Dynamic processing of multi-tiered VAT rate lines (e.g., composite 7% + 19% items).
* 💾 **Balance Verification**: Strict analytical integrity constraints evaluating balancing status ($\text{Debit} == \text{Credit}$).
* 🎨 **Modern UI**: Streamlined native desktop application built via Python's Tkinter utilizing tabbed workflows.
* 🔍 **Debug Tools**: Granular internal toolsets supporting detailed network capturing, DOM tree snapshots, and AngularJS scope monitoring.

---

## Installation

### Prerequisites

* Python 3.8 or higher
* Operating System: Windows 10/11 (fully tested) | Linux & macOS (supported)

### Quick Install

```bash
# Clone or navigate into the repository root
cd Axeane_Desktop_Automation_Tool

# Run the automated bootstrap setup script
# On Windows:
install.bat

# On Linux/macOS:
bash install.sh

```

The script will automatically configure a Python virtual environment, pull required environment specifications via `requirements.txt`, and initialize the local Playwright Chromium binary instance.

### Manual Installation

```bash
# Initialize clean virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Fetch library requirements
pip install -r requirements.txt

# Provision internal Playwright browser binaries
playwright install chromium

```

---

## Usage

### Running the Application

```bash
# Quick-start wrapper (Windows)
run.bat

# Manual direct launch
python run.py

```

### Basic Workflow

1. **Import CSV File**
* Navigate to the **📥 Import Data** tab view.
* Select **Browse CSV/Excel** and choose your raw dataset file.
* Execute by choosing **⚙️ Parse & Apply Rules**. Verify the rows present correctly in the data table matrix.


2. **Review Templates**
* Move to the **🔧 Preview & Rules** tab view.
* Trigger **🔧 Generate Template Cards**.
* Confirm generated metrics look clean: verify grouped invoice counts, total TTC sums, explicit formulas, and look for balanced confirmations ($✓$).


3. **Execute Automation**
* Open the **🏁 Execution & Logs** tab view.
* Configure target browser behavior profiles as needed.
* Click **🚀 Start Automation** to engage the Playwright loop. Watch runtime output logs and track active processing over the real-time progress bar.



### Browser Connection Modes

* **Standard Launch**: Completely fresh, isolated cookie session on each execution cycle.
* **Persistent Profile**: Stores environment footprints inside local cache to keep you logged in between runs (*Recommended*).
* **CDP Connect**: Hooks into a manually opened standalone instance of Chrome or Edge.
* **PWA Mode**: Strips window navigation controls to execute as a minimalist desktop app.

#### Using CDP Connect:

```bash
# Start your local browser engine with debugging exposures enabled
chrome.exe --remote-debugging-port=9222

```

*Manually complete standard login parameters inside the browser window, then select **"Connect to Existing CDP"** inside the application interface.*

---

## Configuration

### Client Profiles (`DB/Vente_Formats.json`)

Manage target routing parameters across various customer types:

```json
{
  "client_profiles": [
    {
      "match": "DEFAULT",
      "compte_client": "411000",
      "use_timbre": true,
      "use_cash": false
    },
    {
      "match": "PASSAGER",
      "compte_client": "411000",
      "use_timbre": true,
      "use_cash": true,
      "compte_caisse": "541100"
    },
    {
      "match": "TUNISIE AUTOMOTIVE",
      "compte_client": "411032",
      "use_timbre": true,
      "use_cash": false
    }
  ]
}

```

### Accounting Rules (`DB/Vente_Rules.json`)

Configure VAT rate accounts and automatic physical stamp fee mappings:

```json
{
  "accounting_logic": {
    "tax_logic": {
      "rates": [
        { "rate": 19, "ht_account": "707019", "tva_account": "436719" },
        { "rate": 7,  "ht_account": "707007", "tva_account": "436707" },
        { "rate": 13, "ht_account": "707013", "tva_account": "436713" }
      ]
    },
    "timbre_fiscal": {
      "default_amount": 1.000,
      "account": "437000",
      "label": "TIMBRE FISCAL"
    }
  }
}

```

---

## CSV Structure

Input transaction files require the following header configuration format:

```text
Client,Operation,Reference,Site,Date,TTC,HT,Remise,NetHT,Fodec,Tot. Net. HT,TVA %,Montant TVA

```

### Data Sample Rows

```text
C000001 | PASSAGER,Facture,FC000761/2026,CPR-LA SOUKRA,02/03/2026,302.080,281.120,28.112,253.008,0,253.008,19.00 %,48.072
C000203 | AUTO CLASSE,Facture,FC000782/2026,CPR-LA SOUKRA,04/03/2026,4871.682,892.960,89.296,803.664,0,803.664,7.00 %,56.256
C000203 | AUTO CLASSE,Facture,FC000782/2026,CPR-LA SOUKRA,04/03/2026,4871.682,3901.598,531.21,3370.388,0,3370.388,19.00 %,640.374

```

> **Data Rules:**
> * **Client Formats**: Strings must explicitly follow the `"CODE | NAME"` formatting style.
> * **Multi-TVA Records**: Related complex invoice line-items split across multiple rows must match reference identifiers perfectly.
> * **Number Presentation**: Use localized comma separations to split thousands, and explicit periods to distinguish decimals.
> * **Percentages**: Ensure value mappings are backed with explicit percentage markers (e.g., `"19.00 %"`).
> 
> 

---

## Building the Standalone Executable

Compile optimized, platform-native application packages directly via the build runner:

```bash
# Compile normal distribution along with a portable standalone ZIP package
python build.py

# Skip portable package creation
python build.py --no-portable

# Produce a raw loose directory output path instead of a compressed singular file
python build.py --no-onefile

# Purge transient operational folders and workspace build artifacts
python build.py --clean

```

* **Output targets location:** Find compiled artifacts inside the `dist/` project subdirectory pathway.

---

## Debugging Subsystems

### Network Logging

Track direct transmission payloads by coupling the interceptor directly to the active Playwright page scope:

```python
from Debug.Network import NetworkInterceptor

network_sniffer = NetworkInterceptor(page)

```

*Inspected metadata captures will dump cleanly into `.json` formats over `Debug/logs/network/`.*

### DOM Snapshots

Save instantaneous visual captures of layout elements to isolate target mapping errors:

```python
from Debug.DOM_Inspector import DOMInspector

inspector = DOMInspector(page)
await inspector.snapshot("#element-id", "snapshot_name")

```

*Outputs trackable HTML files directly to `Debug/logs/dom/`.*

### AngularJS Scope Inspection

Query active variable states hidden inside the AngularJS compilation tree:

```python
from Debug.Angular_Scope import AngularScopeDebugger

debugger = AngularScopeDebugger(page)
value = await debugger.read_scope("#element", "scope.variable")

```

---

## Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    Tkinter Desktop UI                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐   │
│  │ Settings │  │  Import  │  │ Preview  │  │Execute │   │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Business Logic                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ CSV Parser   │  │Formula Engine│  │ Rules Engine │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Browser Automation                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Playwright │  │ JS Elements  │  │    Models    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌────────────────────────┐
              │  Axeane Kompta Web App │
              └────────────────────────┘

```

---

## Performance

* **Automation Velocity**: Web actions parse and post entries at a rate of ~2-3 seconds per invoice cycle.
* **Batch Operations**: A standard batch run of 361 total items finishes within approximately 15-20 minutes.
* **Parser Computation Overhead**: Local CSV and structural formula analysis compute immediately ($<1$ second per 1000 items).
* *Note on API Integrations:* For rapid production scales, avoid UI tracking constraints completely by reviewing logged endpoint routes inside `Debug/Network.py` to write direct backend API injections.

---

## Troubleshooting

> **Issue:** `"No TVA account configured for rate X%"`
> **Solution:** Register the mapping inside your target tax rate array within `DB/Vente_Rules.json`:
> ```json
> { "rate": 13, "ht_account": "707013", "tva_account": "436713" }
> 
> ```
> 
> 

> **Issue:** `"Formula for FC000XXX is NOT balanced"`
> **Solution:** This points to a multi-TVA validation edge case. Check your reference groups and ensure the total debit entry pulls exclusively from the **first row index occurrence**, rather than aggregating rows.

> **Issue:** `Playwright inputs fail to update underlying AngularJS component values`
> **Solution:** Route your target input tasks away from direct text injections. Utilize specific method overrides written inside `Function/JS_Elements.py` to correctly issue the missing native element blur/change updates.

> **Issue:** `CSV parser scans yield empty lists or zero available rows`
> **Solution:** Validate document character encoding sets (verify formats use UTF-8 or UTF-8 with BOM). Ensure structural layout columns align exactly with keywords configured inside `DB/Vente_Structure.json`.

---

## Contributing

This codebase is a proprietary system tool. Internal modifications must conform to the following development conditions:

* Adhere strictly to the defined style guide parameters (explicit function type hints, comprehensive public docstrings).
* Validate changes against the baseline tracking test files.
* Synchronize modifications with documentation file updates.
* Harness standard system wrappers for tracking actions over terminal outputs (`Debug/Logger.py`).

---

## License

Proprietary - All rights reserved.
