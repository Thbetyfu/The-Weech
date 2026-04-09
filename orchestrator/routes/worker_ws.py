"""
Route WebSocket untuk komunikasi Orchestrator ↔ Worker.
Fase 1: Ping-Pong heartbeat + task dispatch sederhana.
"""

import json
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, HTTPException
from pydantic import BaseModel

from core.vault import vault

from core.database import SessionLocal
from core.models import LedgerLog
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

HEARTBEAT_INTERVAL = 15  # detik

async def _record_ledger(worker_id: str, task_id: str, complexity: str, output_length: int):
    # Base reward: Integer only
    credits = 10 if complexity == "EASY" else 50
    # Bonus poin dari kepanjangan response (integer division)
    credits += min(100, output_length // 10)  

    async with SessionLocal() as db:
        try:
            entry = LedgerLog(
                task_id=task_id, 
                worker_id=worker_id, 
                credits_earned=credits,
                complexity=complexity
            )
            db.add(entry)
            await db.commit()
            logger.info(f"💰 Ledger Dicatat: Worker [{worker_id}] mendapat +{credits} kredit! (Tugas: {complexity})")
        except Exception as e:
            logger.error(f"FATAL DB ERROR: Gagal mencatat ledger {task_id}: {e}")
            await db.rollback()


class DispatchRequest(BaseModel):
    prompt: str


@router.post("/api/v1/dispatch")
async def dispatch_task(body: DispatchRequest, request: Request):
    manager = request.app.state.manager

    # Fase 3A: Logika Klasifikasi Beban (Simple Heuristic)
    # Prompt > 200 karakter dikategorikan "HARD" dan wajib diforward ke Node spek tinggi (+ GPU)
    # Jika tidak, berikan ke Node Bronze agar efisiensi ekosistem terjaga
    complexity = "HARD" if len(body.prompt) > 200 else "EASY"
    
    worker = manager.get_best_idle_worker(complexity=complexity)
    if not worker:
        raise HTTPException(status_code=503, detail="No idle workers available")

    # Vault: Create namespace isolasi per request
    task_id = vault.create_session()
    worker.is_busy = True
    worker.current_complexity = complexity

    # Pipa Sanitasi NER untuk anonimisasi identitas (The Vault)
    masked_prompt = vault.mask_text(task_id, body.prompt)

    await worker.websocket.send_text(json.dumps({
        "type": "task",
        "task_id": task_id,
        "prompt": masked_prompt,
    }))

    return {"task_id": task_id, "worker_id": worker.worker_id, "masked_prompt": masked_prompt}


@router.websocket("/ws/worker/{worker_id}")
async def worker_endpoint(websocket: WebSocket, worker_id: str):
    """
    Endpoint WebSocket untuk setiap Worker Node.
    """
    manager = websocket.app.state.manager
    await manager.connect(worker_id, websocket)

    import time
    async def adaptive_ping_loop():
        worker_info = manager.get_worker(worker_id)
        while True:
            if not worker_info:
                break
                
            worker_info.waiting_pong = True
            worker_info.ping_sent_at = time.time()
            try:
                await websocket.send_json({"type": "ping", "ts": worker_info.ping_sent_at})
            except Exception:
                break
            
            timeout = worker_info.get_adaptive_timeout()
            await asyncio.sleep(timeout)
            
            if worker_info.waiting_pong:
                worker_info.missed_pings += 1
                logger.warning(f"⚠️ Worker {worker_id} missed ping (timeout: {timeout:.1f}s). Total missed: {worker_info.missed_pings}/3")
                
                if worker_info.missed_pings >= 3:
                    logger.error(f"❌ Worker {worker_id} ejected due to 3 consecutive missed pings.")
                    try:
                        await websocket.close(code=1011, reason="Heartbeat missed")
                    except Exception:
                        pass
                    break
            
            remainder = HEARTBEAT_INTERVAL - timeout
            if remainder > 0:
                await asyncio.sleep(remainder)

    heartbeat_task = asyncio.create_task(adaptive_ping_loop())

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Non-JSON message from {worker_id}: {raw}")
                continue

            msg_type = msg.get("type")

            if msg_type == "pong":
                ts = msg.get("ts")
                worker_info = manager.get_worker(worker_id)
                if worker_info and worker_info.waiting_pong:
                    worker_info.waiting_pong = False
                    worker_info.missed_pings = 0
                    if ts:
                        rtt = time.time() - float(ts)
                        worker_info.add_rtt(rtt)
                        # logger.debug(f"💓 Pong ← {worker_id} (RTT: {rtt:.3f}s)")

            elif msg_type == "result":
                task_id = msg.get("task_id", "unknown")
                output = msg.get("output", "")
                
                from core.cheat_guard import cheat_guard
                if cheat_guard.is_trap(task_id):
                    # Fase 3D: Cheat Guard Validation
                    passed = cheat_guard.verify_trap(task_id, output)
                    if not passed:
                        # Spoofing detected! Eject Worker
                        logger.error(f"☠️ [BAN] Mengeksekusi Banning pada {worker_id} akibat gagal Cheat Guard.")
                        await manager.disconnect(worker_id)
                        try:
                            await websocket.close()
                        except:
                            pass
                        return # Putus loop Websocket langsung
                    
                    # Worker Jujur -> Berikan bonus eksklusif 
                    worker_info = manager.get_worker(worker_id)
                    if worker_info:
                        worker_info.is_busy = False
                        asyncio.create_task(_record_ledger(worker_id, task_id, "TRAP", 50))
                    continue
                
                # Proses De-masking (The Vault) - mengembalikan text ke nama aslinya
                unmasked_output = vault.unmask_text(task_id, output)
                logger.info(f"🔓 De-masked Result [task={task_id}]: {unmasked_output[:80]}...")
                
                # Stream ke WEB Client (Task D)
                from core.client_manager import client_manager
                await client_manager.stream_to_client(task_id, {
                    "type": "result",
                    "task_id": task_id,
                    "output": unmasked_output
                })

                # Cleanup session Vault setelah task selesai
                vault.cleanup_session(task_id)

                worker_info = manager.get_worker(worker_id)
                comp = "EASY"
                if worker_info:
                    comp = worker_info.current_complexity
                    worker_info.is_busy = False

                # Fase 3B: Catat Pekerjaan ke Ledger (Compute-to-Earn)
                # Dilakukan secara asynchronous agar tidak memblokir event loop ws
                asyncio.create_task(_record_ledger(worker_id, task_id, comp, len(unmasked_output)))

            elif msg_type == "error":
                task_id = msg.get("task_id", "unknown")
                error_msg = msg.get("message", "")
                logger.error(f"❌ Worker {worker_id} failed task {task_id}: {error_msg}")
                
                from core.client_manager import client_manager
                await client_manager.stream_to_client(task_id, {
                    "type": "error",
                    "task_id": task_id,
                    "message": error_msg
                })

                vault.cleanup_session(task_id)
                worker_info = manager.get_worker(worker_id)
                if worker_info:
                    worker_info.is_busy = False

            elif msg_type == "register":
                specs = msg.get("specs", {})
                logger.info(f"📋 Worker {worker_id} registered. Specs: {specs}")
                worker_info = manager.get_worker(worker_id)
                if worker_info:
                    worker_info.specs = specs
            else:
                logger.warning(f"❓ Unknown message type '{msg_type}' from {worker_id}")

    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected for {worker_id}")
    finally:
        heartbeat_task.cancel()
        await manager.disconnect(worker_id)
