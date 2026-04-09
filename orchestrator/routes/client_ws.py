"""
Rute WebSocket khusus untuk API Gateway Frontend (Client).
Menjembatani browser dengan sistem mesh.
"""
import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.client_manager import client_manager

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/client/{task_id}")
async def client_endpoint(websocket: WebSocket, task_id: str):
    """
    Endpoint WebSocket bagi Frontend UI untuk subscribe ke task tertentu.
    Preconditions: task_id tidak boleh kosong.
    """
    if not task_id:
        await websocket.close(code=1008, reason="Task ID missing")
        return

    await websocket.accept()
    await client_manager.register_task(task_id, websocket)

    try:
        # Loop diam hanya untuk menahan koneksi tetap terbuka.
        # Frontend bisa sewaktu-waktu menutupnya.
        while True:
            raw = await websocket.receive_text()
            # Bisa di-expand jika web client ingin membatalkan (abort task)
    except WebSocketDisconnect:
        logger.info(f"🔌 UI Client disconnected from task {task_id}")
    except Exception as e:
        logger.error(f"❌ Error pada client websocket (task={task_id}): {e}")
    finally:
        # Error Handling & Cleanup (Defensive)
        await client_manager.unregister_task(task_id)
        logger.debug(f"🧹 Dihapus binding UI untuk task {task_id}")
