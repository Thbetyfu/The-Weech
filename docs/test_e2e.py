import asyncio
import json
import time
import httpx


ORCHESTRATOR_URL = "http://localhost:8000"


async def test_health():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ORCHESTRATOR_URL}/health")
        data = resp.json()
        assert data["status"] == "ok", "❌ Orchestrator tidak sehat"
        print(f"✅ Health OK — {data['active_workers']} worker aktif")
        return data["active_workers"]


async def test_dispatch(prompt: str = "Sebutkan 3 strategi konten untuk kreator teknologi."):
    async with httpx.AsyncClient(timeout=60.0) as client:
        start = time.monotonic()
        resp = await client.post(
            f"{ORCHESTRATOR_URL}/api/v1/dispatch",
            json={"prompt": prompt},
        )

        if resp.status_code == 503:
            print("⚠️ Tidak ada Worker idle. Pastikan worker.py sudah berjalan.")
            return

        data = resp.json()
        elapsed = time.monotonic() - start
        print(f"✅ Task dispatched: {data['task_id']} → Worker: {data['worker_id']}")
        print(f"   Waktu dispatch: {elapsed:.2f}s")


async def main():
    print("=" * 50)
    print("TheWeech End-to-End Test")
    print("=" * 50)

    workers = await test_health()
    if workers == 0:
        print("⚠️ Tidak ada worker. Jalankan worker.py di terminal lain dulu.")
        return

    await test_dispatch()


if __name__ == "__main__":
    asyncio.run(main())
