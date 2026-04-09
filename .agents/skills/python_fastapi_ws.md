---
name: python_fastapi_ws
description: >
  Pattern FastAPI + WebSocket yang dipakai di Orchestrator TheWeech.
  Berisi template kode, cara menambah route baru, cara inject dependency,
  dan cara handle concurrent WebSocket connections dengan benar.
---

# FastAPI + WebSocket Skill

## Cara Menambah Route Baru ke Orchestrator

### 1. Buat file di `orchestrator/routes/nama_route.py`

```python
"""
Deskripsi singkat route ini.
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db

router = APIRouter(prefix="/api/v1", tags=["NamaTag"])


@router.get("/endpoint")
async def nama_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    manager = request.app.state.manager  # akses ConnectionManager
    return {"status": "ok"}
```

### 2. Daftarkan di `orchestrator/main.py`

```python
from routes.nama_route import router as nama_router
app.include_router(nama_router)
```

---

## Cara Mengirim Task ke Worker dari Route HTTP

```python
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import uuid

router = APIRouter()


class DispatchRequest(BaseModel):
    prompt: str


@router.post("/api/v1/dispatch")
async def dispatch_task(body: DispatchRequest, request: Request):
    manager = request.app.state.manager

    worker = manager.get_idle_worker()
    if not worker:
        raise HTTPException(status_code=503, detail="No idle workers available")

    task_id = str(uuid.uuid4())
    worker.is_busy = True

    await worker.websocket.send_json({
        "type": "task",
        "task_id": task_id,
        "prompt": body.prompt,
    })

    return {"task_id": task_id, "worker_id": worker.worker_id}
```

---

## Pattern WebSocket dengan Timeout (Anti-Zombie Connection)

```python
import asyncio
from fastapi import WebSocket, WebSocketDisconnect


async def safe_receive(websocket: WebSocket, timeout: float = 30.0):
    """Terima pesan dengan timeout — cegah zombie connection."""
    try:
        return await asyncio.wait_for(websocket.receive_text(), timeout=timeout)
    except asyncio.TimeoutError:
        await websocket.close(code=1000, reason="Receive timeout")
        return None
```

---

## Pattern Broadcast ke Semua Worker

```python
async def broadcast_to_all(manager, message: dict) -> None:
    """Kirim pesan ke semua Worker yang aktif."""
    disconnected = []
    for worker in manager.get_all_workers():
        try:
            await worker.websocket.send_json(message)
        except Exception:
            disconnected.append(worker.worker_id)

    # Cleanup zombie connections
    for wid in disconnected:
        await manager.disconnect(wid)
```

---

## Pattern Response Model (Pydantic)

Selalu gunakan Pydantic model untuk response agar terdokumentasi di Swagger:

```python
from pydantic import BaseModel


class WorkerStatus(BaseModel):
    worker_id: str
    is_busy: bool
    tasks_completed: int


class HealthResponse(BaseModel):
    status: str
    active_workers: int
    workers: list[WorkerStatus]
```

---

## Hal yang Harus Dihindari

| ❌ Jangan | ✅ Gunakan |
|-----------|------------|
| `import time; time.sleep(N)` | `await asyncio.sleep(N)` |
| `requests.get(url)` | `async with httpx.AsyncClient() as c: await c.get(url)` |
| `print(...)` | `logger.info(...)` |
| Hardcode port/URL | Baca dari `settings.XXX` |
| Bare `except:` | `except SpecificException as e:` |
| Global mutable state | Simpan di `app.state.xxx` |
