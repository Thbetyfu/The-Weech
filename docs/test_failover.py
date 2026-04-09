import asyncio
import httpx
import websockets
import time

ORCHESTRATOR_WS_URL = "ws://127.0.0.1:8000/ws/worker"
ORCHESTRATOR_API = "http://127.0.0.1:8000"

async def check_workers():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ORCHESTRATOR_API}/health")
        return resp.json()["active_workers"]

async def zombie_worker_simulation():
    print("🧟 Memulai Simulasi Zombie Worker (Simulasi Indihome / ISP Putus Tiba-tiba)")
    
    # 1. Connect normally
    ws = await websockets.connect(f"{ORCHESTRATOR_WS_URL}/zombie-001")
    print("✅ Zombie Worker 'zombie-001' Connected")
    
    initial_count = await check_workers()
    print(f"📊 Active Workers di Orchestrator: {initial_count}")

    print("🔌 Memutus paksa socket zombie TANPA pemberitahuan (Simulasi Kabel RJ45 dicabut)...")
    # Kita tidak mengirim frame penutupan standar (close frame) agar server tidak tahu secara langsung
    # websockets tidak memiliki fungsi 'hard abort', jadi kita sengaja menimbulkan panic:
    ws.transport.abort()
    
    start_time = time.monotonic()
    
    print("⏳ Menunggu Orchestrator mendeteksi dan melakukan mekanisme Eject...")
    while True:
        current_count = await check_workers()
        if current_count < initial_count:
            elapsed = time.monotonic() - start_time
            print(f"🚨 BOOM! Orchestrator berhasil mendeteksi dan eject Zombie Worker.")
            print(f"⏱️ Waktu Deteksi Failover: {elapsed:.2f} detik")
            break
        await asyncio.sleep(1)
        if time.monotonic() - start_time > 45:
            print("❌ FAIL: Orchestrator gagal mendeteksi Zombie Connection (Memory Leak!)")
            break

if __name__ == "__main__":
    asyncio.run(zombie_worker_simulation())
