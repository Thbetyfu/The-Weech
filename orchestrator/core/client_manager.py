"""
Client Connection Manager (API Gateway layer).
Mengelola koneksi WebSocket dari Web Frontend (Client) ke Orchestrator.
Tujuan: Mengirim balik stream hasil inferensi dari Worker secara asinkron.
"""
import asyncio
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ClientManager:
    def __init__(self):
        # task_id -> WebSocket (Client yang me-request task tersebut)
        self.active_tasks = {}
        self._lock = asyncio.Lock()

    async def register_task(self, task_id: str, websocket: WebSocket):
        """
        Mendaftarkan WebSocket klien untuk menerima update dari suatu task_id.
        Precondition: task_id dan websocket tidak boleh None.
        """
        if not task_id or not websocket:
            raise ValueError("task_id dan websocket wajib diisi.")
            
        async with self._lock:
            self.active_tasks[task_id] = websocket
        logger.debug(f"🖥️ Client registered for task: {task_id}")

    async def unregister_task(self, task_id: str):
        """Menghapus mapping klien untuk mencegah memory leak."""
        async with self._lock:
            self.active_tasks.pop(task_id, None)

    async def stream_to_client(self, task_id: str, data: dict):
        """
        Mengirim payload data ke klien secara real-time.
        Error Handling: Jika klien terputus, silent catch (graceful fallback) dan hapus dari task.
        """
        websocket = self.active_tasks.get(task_id)
        if not websocket:
            # Client mungkin sudah disconnect duluan
            return

        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.warning(f"⚠️ Gagal mengirim stream ke client untuk task {task_id}: {e}")
            await self.unregister_task(task_id)

client_manager = ClientManager()
