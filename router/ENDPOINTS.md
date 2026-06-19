---

# ENDPOINTS.md - API Specifications & Integration Guide

This document defines the REST API layer exposing the Axeane Kompta Desktop Automation Engine. This standalone endpoint gateway enables decouple interfaces (React, Vue, mobile wrappers, or headless triggers) to manage session lifecycles, data transformations, and system automation tasks.

---

## 1. Quick Start & Execution

### System Requirements

Verify that your environmental specifications have been updated to support FastAPI server networking modules:

```text
playwright>=1.40.0
httpx>=0.25.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
pydantic>=2.5.0

```

### Server Deployment

Run the automated startup script wrapper (Windows systems):

```bash
run_api.bat

```

Alternatively, invoke the server directly using your virtual environment executable engine:

```bash
# Direct python wrapper launch
python endpoint.py

# Manual Uvicorn worker allocation
uvicorn endpoint:app --reload --host 0.0.0.0 --port 8000

```

* **Interactive OpenAPI Specs (Swagger UI):** `http://localhost:8000/docs`
* **Alternative Static Specifications (ReDoc):** `http://localhost:8000/redoc`

---

## 2. Structural Architecture

```text
       Frontend App                     FastAPI Server                  Worker / Engine
            │                                 │                                │
            │─── POST /api/upload ───────────►│                                │
            │◄── (session_id) ────────────────│                                │
            │                                 │                                │
            │─── POST /api/parse ────────────►│─── (Spawns background task) ──►│
            │◄── (202 Accepted) ──────────────│                                │
            │                                 │◄── updates state data ─────────│
            │─── GET /api/status ────────────►│                                │
            │◄── status: "completed" ─────────│                                │
            │                                 │                                │
            │─── POST /api/execute ──────────►│─── (Spawns browser driver) ───►│
            │◄── (202 Accepted) ──────────────│                                │
            │                                 │◄── streams execution progress ─│
            ▼                                 ▼                                ▼

```

---

## 3. Core Endpoint Specifications

All response payloads match Content-Type `application/json`. The gateway utilizes background task execution boundaries to handle intensive operations without disconnecting active connections.

### System Endpoints

* **`GET /health`**
* **Description:** Performs a system validation check on engine components.
* **Success Response (`200 OK`):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-06-19T08:44:18.123456"
}

```





### Import & Parsing Subsystems

* **`POST /api/upload`**
* **Description:** Streams a raw invoice `.csv` transaction ledger into session isolation spaces.
* **Payload Configuration:** Form data field `file: UploadFile` binary stream.
* **Success Response (`200 OK`):**
```json
{
  "session_id": "4a7b1892-bf72-4d76-9281-a90f12c34912",
  "filename": "journal_vte_mars_26.csv",
  "row_count": 366,
  "message": "File uploaded successfully"
}

```




* **`POST /api/parse`**
* **Description:** Extracts properties from localized assets and populates calculation vectors inside a background process.
* **Request Body Layout:**
```json
{
  "session_id": "4a7b1892-bf72-4d76-9281-a90f12c34912",
  "doc_type": "Vente"
}

```


* **Success Response (`202 Accepted`):**
```json
{
  "status": "parsing",
  "message": "Parsing started in background"
}

```





### Accounting Formula Preview Engine

* **`GET /api/formulas`**
* **Description:** Pulls compiled groupings and accounting profiles generated during parsing steps.
* **Query Parameter:** `session_id=UUID`
* **Success Response (`200 OK`):**
```json
{
  "session_id": "4a7b1892-bf72-4d76-9281-a90f12c34912",
  "total_cards": 4,
  "total_rows": 361,
  "balanced_cards": 4,
  "unbalanced_cards": 0,
  "cards": [
    {
      "ref": "FC000761/2026",
      "match_key": "PASSAGER",
      "match_type": "substring",
      "row_count": 1,
      "total_ttc": 302.080,
      "tva_rates": [19.0],
      "is_balanced": true,
      "formula_lines": [...],
      "sample_client": "C000001 | PASSAGER"
    }
  ]
}

```




* **`GET /api/formulas/{ref}`**
* **Description:** Inspects configuration metrics bound to a single transaction reference ID.
* **Query Parameter:** `session_id=UUID`



### Automation Task Controllers

* **`POST /api/execute`**
* **Description:** Launches the automated Playwright engine sequence.
* **Request Body Layout:**
```json
{
  "session_id": "4a7b1892-bf72-4d76-9281-a90f12c34912",
  "mode": "dry_run", 
  "browser_mode": "headless" 
}

```


* *Options:* `mode`: `dry_run` | `live` ; `browser_mode`: `headless` | `visible`


* **Success Response (`202 Accepted`):**
```json
{
  "status": "executing",
  "message": "Execution started in background"
}

```




* **`GET /api/status`**
* **Description:** Monitors asynchronous background loops, providing detailed execution tracking matrices.
* **Query Parameter:** `session_id=UUID`
* **Success Response (`200 OK`):**
```json
{
  "session_id": "4a7b1892-bf72-4d76-9281-a90f12c34912",
  "status": "executing",
  "progress": {
    "current": 45,
    "total": 361,
    "current_ref": "FC000812/2026",
    "percentage": 12.46
  },
  "last_error": null,
  "logs": [...]
}

```




* **`POST /api/stop`**
* **Description:** Issues interrupt routines forcing browser runtime instances to drop active loops safely.
* **Query Parameter:** `session_id=UUID`



---

## 4. Frontend Integration Blueprint

Below is an abstract reference module demonstrating state tracking, data injection, and polling behaviors using native browser API wrappers.

```javascript
/**
 * Orchestrator API abstraction class for interaction with Axeane API gateways.
 */
class AxeaneAutomationDriver {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.sessionId = null;
  }

  /**
   * Dispatches binary payloads to the data layer storage system.
   */
  async uploadDataset(fileObject) {
    const payloadBuffer = new FormData();
    payloadBuffer.append('file', fileObject);

    const connection = await fetch(`${this.baseURL}/api/upload`, {
      method: 'POST',
      body: payloadBuffer
    });
    
    const extraction = await connection.json();
    this.sessionId = extraction.session_id;
    return extraction;
  }

  /**
   * Initializes structural data checks and handles pooling routines.
   */
  async triggerAnalysis(onProgressUpdate) {
    if (!this.sessionId) throw new Error('Active session contexts missing.');

    await fetch(`${this.baseURL}/api/parse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: this.sessionId, doc_type: 'Vente' })
    });

    return new Promise((resolve, reject) => {
      const trackingThread = setInterval(async () => {
        try {
          const check = await fetch(`${this.baseURL}/api/status?session_id=${this.sessionId}`);
          const stateData = await check.json();
          
          if (onProgressUpdate) onProgressUpdate(stateData);

          if (stateData.status === 'completed') {
            clearInterval(trackingThread);
            
            // Extract analytical compilation blocks
            const catalog = await fetch(`${this.baseURL}/api/formulas?session_id=${this.sessionId}`);
            resolve(await catalog.json());
          } else if (stateData.status === 'error') {
            clearInterval(trackingThread);
            reject(new Error(stateData.last_error || 'Asynchronous verification broken.'));
          }
        } catch (connectionError) {
          clearInterval(trackingThread);
          reject(connectionError);
        }
      }, 1000);
    });
  }

  /**
   * Instructs the engine to execute browser injection loops.
   */
  async launchAutomationEngine(liveExecution = false) {
    const executionProfile = await fetch(`${this.baseURL}/api/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: this.sessionId,
        mode: liveExecution ? 'live' : 'dry_run',
        browser_mode: 'headless'
      })
    });
    return await executionProfile.json();
  }
}

```

---

## 5. Security & Session Bounds

* **Workspace Sanitization:** Invoking `DELETE /api/session/{session_id}` deletes local document assets from disk and unloads memory states instantly.
* **Network Isolation Constraints:** Access control properties are pre-configured to generic wildcards (`allow_origins=["*"]`). Prior to enterprise staging, restrict parameters inside `endpoint.py` to your specific front-end deployment origin points.
* **Worker Execution Health:** State variables utilize standard memory scopes. Avoid scaling multiple simultaneous processes on individual system hardware profiles without configuring isolated database worker engines.
