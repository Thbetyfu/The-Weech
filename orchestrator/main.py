"""
TheWeech Orchestrator — Entry Point
Fase 1: PoC lokal (WebSocket + Ollama Worker)
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import json

from core.config import settings
from core.database import init_db
from core.connection_manager import ConnectionManager
from routes.worker_ws import router as worker_ws_router
from routes.client_ws import router as client_ws_router
from routes.health import router as health_router
from routes.wallet import router as wallet_router
from routes.b2b_agency import router as b2b_agency_router

# Setup templates
templates = Jinja2Templates(directory="templates")

from core.cheat_guard import cheat_guard
import asyncio

async def trap_dispatcher(manager: ConnectionManager):
    """Fase 3D: Rutinitas periodik yang mengirimkan Trap Task (Jebakan Anti-Spoof) ke idle Worker."""
    while True:
        await asyncio.sleep(60) # Cek setiap 60 detik (Interval disesuaikan untuk POC) # TODO: revert to longer if needed
        # Cari satu idle worker secara acak (karena ini hanya inspeksi berkala)
        worker = manager.get_best_idle_worker(complexity="EASY")
        if worker:
            prompt, expected = cheat_guard.generate_trap()
            import uuid
            trap_id = f"trap-{uuid.uuid4()}"
            
            cheat_guard.register_trap(trap_id, worker.worker_id, expected)
            worker.is_busy = True
            
            try:
                await worker.websocket.send_text(json.dumps({
                    "type": "task",
                    "task_id": trap_id,
                    "prompt": prompt,
                }))
                print(f"🎣 [CHEAT GUARD] Umpan diterjunkan ke {worker.worker_id}")
            except Exception as e:
                worker.is_busy = False

async def ledger_flusher(manager: ConnectionManager):
    """
    Fase Penambalan: Menulis Buffer Credits ke Disk (SQLite) secara batch
    untuk menghilangkan Database Write Locking pada saat traffic Worker tinggi.
    """
    from routes.worker_ws import _record_ledger
    import uuid
    while True:
        await asyncio.sleep(15) # Flush setiap 15 detik (di POC)
        for worker in list(manager._workers.values()):
            if worker.pending_credits > 0:
                pts = worker.pending_credits
                worker.pending_credits = 0  # Reset in memory buffer
                
                # Fase 5B: Pemisahan Jalur Distribusi (Discount vs Biasa)
                target_id = worker.worker_id
                if worker.is_enterprise and worker.agency_api_key:
                    target_id = f"B2B:{worker.agency_api_key}"

                asyncio.create_task(_record_ledger(
                    worker_id=target_id,
                    task_id=f"batch-{uuid.uuid4()}",
                    complexity="BATCH",
                    output_length=(pts - 10) * 10 # Dummy calc back
                ))
                # Di produksi aslinya _record_ledger bisa dimodifikasi agar langsung accept param 'credits_earned'
                # tapi kita akali parameter output_length untuk POC agar menembus rumus.

# --------------------------------------------------------------------------- #
# Lifespan — setup & teardown
# --------------------------------------------------------------------------- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 TheWeech Orchestrator starting on {settings.HOST}:{settings.PORT}")
    await init_db()
    print("✅ Database initialized")
    
    # Shared connection manager
    manager = ConnectionManager()
    app.state.manager = manager
    
    # Start Routine Cheat Guard & Ledger Flusher
    bg_task = asyncio.create_task(trap_dispatcher(manager))
    flush_task = asyncio.create_task(ledger_flusher(manager))
    
    yield
    print("🛑 Orchestrator shutting down...")
    bg_task.cancel()
    flush_task.cancel()
    await manager.disconnect_all()


# --------------------------------------------------------------------------- #
# App instance
# --------------------------------------------------------------------------- #
app = FastAPI(
    title="TheWeech Orchestrator",
    description="Pusat komando AI Mesh TheWeech — Fase 1 PoC",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mounting static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Shared connection manager (diinjeksi ke semua route)
manager = ConnectionManager()
app.state.manager = manager

# Routes
@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Serve the premium monitoring dashboard."""
    return templates.TemplateResponse(
        "creator/index.html", 
        {
            "request": request, 
            "active_workers": len(request.app.state.manager.active_connections)
        }
    )

app.include_router(health_router)
app.include_router(worker_ws_router)
app.include_router(client_ws_router)
app.include_router(wallet_router)
app.include_router(b2b_agency_router)

# --------------------------------------------------------------------------- #
# Run
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )
