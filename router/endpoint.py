# endpoint.py
"""
Axeane Kompta Automation Engine - REST API
Exposes the automation engine to frontend applications.

Run with: uvicorn endpoint:app --reload --port 8000
Docs at: http://localhost:8000/docs
"""
import os
import sys
import json
import uuid
import shutil
import asyncio
import threading
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from Function.csv_parser import parse_bank_csv, parse_bank_pdf, parse_vente_csv
from Modules.FormulaEngine import FormulaEngine
from Debug.Logger import ColorLogger as log

# ============================================================================
# APP INITIALIZATION
# ============================================================================
app = FastAPI(
    title="Axeane Kompta Automation API",
    description="REST API for Axeane Kompta accounting automation engine",
    version="1.0.0",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# SHARED STATE MANAGEMENT
# ============================================================================
class AppState:
    """Singleton state manager for the automation engine."""
    
    def __init__(self):
        self.reset()
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        self.logs_dir = Path("api_logs")
        self.logs_dir.mkdir(exist_ok=True)
    
    def reset(self):
        """Reset state to initial values."""
        self.current_session_id: Optional[str] = None
        self.raw_data: List[Dict] = []
        self.formula_cards: List[Dict] = []
        self.execution_status: str = "idle"  # idle, parsing, executing, completed, error
        self.execution_progress: Dict = {}
        self.logs: List[Dict] = []
        self.last_error: Optional[str] = None
    
    def add_log(self, level: str, message: str):
        """Add a log entry."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
        }
        self.logs.append(entry)
        # Keep only last 1000 logs
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]

# Global state instance
state = AppState()

# ============================================================================
# PYDANTIC MODELS
# ============================================================================
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

class UploadResponse(BaseModel):
    session_id: str
    filename: str
    row_count: int
    message: str

class ParseRequest(BaseModel):
    session_id: str
    doc_type: str = "Vente"

class FormulaCard(BaseModel):
    ref: str
    match_key: str
    match_type: str
    row_count: int
    total_ttc: float
    tva_rates: List[float]
    is_balanced: bool
    formula_lines: List[Dict]
    sample_client: Optional[str] = None
    doc_type: Optional[str] = "Vente"
    total_amount: Optional[float] = None
    signed_amount: Optional[float] = None
    category: Optional[str] = None
    journal: Optional[str] = None

class FormulasResponse(BaseModel):
    session_id: str
    total_cards: int
    total_rows: int
    balanced_cards: int
    unbalanced_cards: int
    cards: List[FormulaCard]

class ExecuteRequest(BaseModel):
    session_id: str
    mode: str = "dry_run"  # dry_run, live
    browser_mode: str = "headless"  # headless, visible

class ExecutionStatus(BaseModel):
    session_id: str
    status: str
    progress: Dict[str, Any]
    last_error: Optional[str]
    logs: List[Dict]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_session_path(session_id: str) -> Path:
    """Get the path for a session's uploaded file."""
    session_dir = state.upload_dir / session_id
    if not session_dir.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    
    uploaded_files = [
        p for p in session_dir.iterdir()
        if p.is_file() and p.suffix.lower() in {".csv", ".pdf"}
    ]
    if not uploaded_files:
        raise HTTPException(status_code=404, detail="No import file found for session")
    
    return uploaded_files[0]

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
    )

@app.post("/api/upload", response_model=UploadResponse, tags=["Import"])
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file for processing.
    Returns a session_id that must be used in subsequent requests.
    """
    extension = Path(file.filename).suffix.lower()
    if extension not in {'.csv', '.pdf'}:
        raise HTTPException(status_code=400, detail="Only CSV and PDF files are allowed")
    
    # Create new session
    session_id = str(uuid.uuid4())
    session_dir = state.upload_dir / session_id
    session_dir.mkdir(exist_ok=True)
    
    # Save file
    file_path = session_dir / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Quick row/page count
    if extension == ".csv":
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            row_count = sum(1 for _ in f) - 1  # Subtract header
    else:
        row_count = 0
    
    state.current_session_id = session_id
    state.reset()
    state.current_session_id = session_id
    
    return UploadResponse(
        session_id=session_id,
        filename=file.filename,
        row_count=row_count,
        message="File uploaded successfully",
    )

@app.post("/api/parse", tags=["Import"])
async def parse_csv(request: ParseRequest, background_tasks: BackgroundTasks):
    """
    Parse the uploaded CSV and generate formula cards.
    This runs in the background and updates the execution status.
    """
    if request.session_id != state.current_session_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state.execution_status = "parsing"
    state.add_log("INFO", "Starting CSV parsing...")
    
    async def parse_task():
        try:
            file_path = get_session_path(request.session_id)
            
            doc_type = request.doc_type.strip().lower()
            if doc_type not in {"vente", "bank", "banque"}:
                raise ValueError(f"Unsupported doc_type: {request.doc_type}")

            is_bank = doc_type in {"bank", "banque"}
            is_pdf = file_path.suffix.lower() == ".pdf"

            if is_pdf and not is_bank:
                raise ValueError("PDF parsing is currently supported for Bank documents only.")

            # Parse source file (run in thread to avoid blocking)
            loop = asyncio.get_event_loop()
            raw_data, _ = await loop.run_in_executor(
                None, 
                lambda: parse_bank_pdf(str(file_path)) if is_pdf else (
                    parse_bank_csv(str(file_path)) if is_bank else parse_vente_csv(str(file_path))
                )
            )
            
            state.raw_data = raw_data
            state.add_log("SUCCESS", f"Parsed {len(raw_data)} rows")
            
            # Generate formulas
            state.add_log("INFO", "Generating formula cards...")
            engine = FormulaEngine()
            cards = engine.build_bank_cards(raw_data) if is_bank else engine.build_cards(raw_data)
            
            state.formula_cards = cards
            state.execution_status = "completed"
            
            # Summary
            balanced = sum(1 for c in cards if c.get("is_balanced", False))
            state.add_log("SUCCESS", 
                f"Generated {len(cards)} formula cards "
                f"({balanced} balanced, {len(cards) - balanced} unbalanced)"
            )
            
        except Exception as e:
            state.execution_status = "error"
            state.last_error = str(e)
            state.add_log("ERROR", f"Parse failed: {str(e)}")
    
    background_tasks.add_task(parse_task)
    
    return {"status": "parsing", "message": "Parsing started in background"}

@app.get("/api/formulas", response_model=FormulasResponse, tags=["Formulas"])
async def get_formulas(session_id: str = Query(...)):
    """Get all formula cards for a session."""
    if session_id != state.current_session_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not state.formula_cards:
        raise HTTPException(status_code=404, detail="No formulas generated yet")
    
    # Calculate summary
    total_rows = sum(c.get("row_count", 0) for c in state.formula_cards)
    balanced = sum(1 for c in state.formula_cards if c.get("is_balanced", False))
    
    return FormulasResponse(
        session_id=session_id,
        total_cards=len(state.formula_cards),
        total_rows=total_rows,
        balanced_cards=balanced,
        unbalanced_cards=len(state.formula_cards) - balanced,
        cards=[FormulaCard(**card) for card in state.formula_cards],
    )

@app.get("/api/formulas/{ref}", tags=["Formulas"])
async def get_formula_by_ref(ref: str, session_id: str = Query(...)):
    """Get a specific formula card by reference."""
    if session_id != state.current_session_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    for card in state.formula_cards:
        if card.get("ref") == ref:
            return card
    
    raise HTTPException(status_code=404, detail=f"Formula {ref} not found")

@app.post("/api/execute", tags=["Execution"])
async def execute_automation(request: ExecuteRequest, background_tasks: BackgroundTasks):
    """
    Start the automation process.
    - mode: 'dry_run' (simulate) or 'live' (actually fill forms)
    - browser_mode: 'headless' or 'visible'
    """
    if request.session_id != state.current_session_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not state.formula_cards:
        raise HTTPException(status_code=400, detail="No formulas to execute")
    
    if state.execution_status == "executing":
        raise HTTPException(status_code=409, detail="Execution already in progress")
    
    state.execution_status = "executing"
    state.add_log("INFO", f"Starting execution in {request.mode} mode...")
    
    async def execute_task():
        try:
            # TODO: Implement actual execution logic
            # This would use the existing Modules/AxeaneOrchestrator.py
            # For now, simulate execution
            
            total = len(state.formula_cards)
            for i, card in enumerate(state.formula_cards):
                state.execution_progress = {
                    "current": i + 1,
                    "total": total,
                    "current_ref": card.get("ref"),
                    "percentage": ((i + 1) / total) * 100,
                }
                state.add_log("INFO", 
                    f"[{i+1}/{total}] Processing {card.get('ref')} "
                    f"(TTC: {card.get('total_ttc', 0):.3f})"
                )
                
                # Simulate processing time
                await asyncio.sleep(0.5)
                
                # In live mode, would call:
                # await orchestrator.fill_one_invoice(card, profile)
            
            state.execution_status = "completed"
            state.add_log("SUCCESS", f"Execution completed: {total} invoices processed")
            
        except Exception as e:
            state.execution_status = "error"
            state.last_error = str(e)
            state.add_log("ERROR", f"Execution failed: {str(e)}")
    
    background_tasks.add_task(execute_task)
    
    return {"status": "executing", "message": "Execution started in background"}

@app.get("/api/status", response_model=ExecutionStatus, tags=["Execution"])
async def get_status(session_id: str = Query(...)):
    """Get the current execution status."""
    if session_id != state.current_session_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return ExecutionStatus(
        session_id=session_id,
        status=state.execution_status,
        progress=state.execution_progress,
        last_error=state.last_error,
        logs=state.logs[-100:],  # Last 100 logs
    )

@app.post("/api/stop", tags=["Execution"])
async def stop_execution(session_id: str = Query(...)):
    """Stop the current execution."""
    if session_id != state.current_session_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if state.execution_status != "executing":
        raise HTTPException(status_code=400, detail="No execution in progress")
    
    # TODO: Implement actual stop logic
    # Would need to signal the orchestrator to stop
    state.execution_status = "idle"
    state.add_log("WARNING", "Execution stopped by user")
    
    return {"status": "stopped", "message": "Execution stopped"}

@app.get("/api/logs", tags=["System"])
async def get_logs(
    session_id: str = Query(...),
    limit: int = Query(100, ge=1, le=1000),
    level: Optional[str] = Query(None),
):
    """Get logs for a session."""
    if session_id != state.current_session_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    logs = state.logs[-limit:]
    
    if level:
        logs = [log for log in logs if log.get("level") == level.upper()]
    
    return {"logs": logs, "count": len(logs)}

@app.delete("/api/session/{session_id}", tags=["System"])
async def delete_session(session_id: str):
    """Delete a session and its uploaded files."""
    if session_id != state.current_session_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Delete uploaded files
    session_dir = state.upload_dir / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir)
    
    # Reset state
    state.reset()
    
    return {"status": "deleted", "message": "Session deleted"}

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
