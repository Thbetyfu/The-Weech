"""
Connection Manager — mengelola semua koneksi WebSocket Worker aktif.
Thread-safe untuk concurrent Worker connections.
"""

import asyncio
from typing import Dict
from fastapi import WebSocket

import logging

logger = logging.getLogger(__name__)


class WorkerInfo:
    """Metadata satu Worker yang sedang terkoneksi."""

    def __init__(self, worker_id: str, websocket: WebSocket):
        self.worker_id = worker_id
        self.websocket = websocket
        self.is_busy: bool = False
        self.tasks_completed: int = 0
        self.specs: dict = {}
        self.current_complexity: str = "EASY"
        
        # Adaptive Heartbeat Stats (Sprint 2B)
        self.rtt_history: list[float] = []
        self.waiting_pong: bool = False
        self.ping_sent_at: float = 0.0
        self.missed_pings: int = 0

    def add_rtt(self, rtt: float):
        self.rtt_history.append(rtt)
        if len(self.rtt_history) > 10:
            self.rtt_history.pop(0)

    def get_adaptive_timeout(self) -> float:
        """
        Hitung timeout berdasarkan RTT x 3 (Min 3s, Max 12s)
        Sesuai spesifikasi Sprint 2B untuk ISP seluler Indonesia.
        """
        if not self.rtt_history:
            return 3.0  # Default koneksi pertama
        avg_rtt = sum(self.rtt_history) / len(self.rtt_history)
        timeout = avg_rtt * 3.0
        return max(3.0, min(timeout, 12.0))

    def __repr__(self) -> str:
        return f"<Worker id={self.worker_id} busy={self.is_busy} timeout={self.get_adaptive_timeout():.1f}s>"


class ConnectionManager:
    """
    Pusat manajemen koneksi WebSocket semua Worker.
    Fase 1: in-memory dict, Fase 5+ akan diganti distributed state.
    """

    def __init__(self):
        # worker_id → WorkerInfo
        self._workers: Dict[str, WorkerInfo] = {}
        self._lock = asyncio.Lock()

    async def connect(self, worker_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._workers[worker_id] = WorkerInfo(worker_id, websocket)
        logger.info(f"✅ Worker '{worker_id}' connected. Total: {len(self._workers)}")

    async def disconnect(self, worker_id: str) -> None:
        async with self._lock:
            self._workers.pop(worker_id, None)
        logger.info(f"❌ Worker '{worker_id}' disconnected. Total: {len(self._workers)}")

    def get_best_idle_worker(self, complexity: str = "EASY") -> WorkerInfo | None:
        """
        Smart Routing Engine (Fase 3 Task A):
        Memilih Worker idle yang paling cocok berdasarkan beban tugas (prompt).
        - Tugas HARD (Prompt panjang): Ambil Worker kasta Gold (Skor hardware tertinggi).
        - Tugas EASY (Prompt pendek): Ambil Worker kasta Bronze (Skor hardware terendah) 
          untuk menghindari mubazir / starvation pada mesin spek rendah.
        """
        idles = [w for w in self._workers.values() if not w.is_busy]
        if not idles:
            return None

        # Precondition/Defensive: Hitung skor dengan aman, antisipasi spoof data 'Unknown'
        def calculate_power_score(w: WorkerInfo) -> float:
            try:
                cores = w.specs.get("cpu_cores", 2)
                ram = w.specs.get("ram_gb", 4.0)
                
                # Jika string 'Unknown' dll, fallback ke minimum requirement
                cores = float(cores) if str(cores).replace('.','').isdigit() else 2.0
                ram = float(ram) if str(ram).replace('.','').isdigit() else 4.0
                
                return cores + (ram / 2.0)
            except Exception as e:
                logger.error(f"Error parse specs for {w.worker_id}: {e}")
                return 0.0

        idles.sort(key=calculate_power_score, reverse=True) # Descending (Kuat -> Lemah)

        if complexity == "HARD":
            return idles[0] # Ambil yang terkuat
        else:
            return idles[-1] # Ambil yang terlemah (Resource efficiency)

    def get_worker(self, worker_id: str) -> WorkerInfo | None:
        return self._workers.get(worker_id)

    def get_all_workers(self) -> list[WorkerInfo]:
        return list(self._workers.values())

    @property
    def active_count(self) -> int:
        return len(self._workers)
