---
name: testing_strategy
description: >
  Strategi QA dan testing setiap komponen TheWeech. Berisi cara test
  WebSocket, cara test Ollama integration, cara ukur KPI Fase 1,
  dan script pengujian yang siap dipakai.
---

# Testing Strategy Skill

## Hierarki Test di TheWeech

```
Fase 1 PoC:
  1. Manual test (curl, wscat)     ← SEKARANG
  2. Script Python otomatis        ← Sprint 1F
  
Fase 2+:
  3. pytest + pytest-asyncio       ← Setelah PoC stabil
  4. Load testing (locust)         ← Sebelum deploy cloud
```

---

## Test 1: Health Check Orchestrator

```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "TheWeech Orchestrator",
  "version": "0.1.0",
  "active_workers": 0,
  "workers": []
}
```

---

## Test 2: WebSocket Connection (Manual)

Install `wscat` jika belum ada:
```powershell
npm install -g wscat
```

Test koneksi Worker:
```powershell
wscat -c ws://localhost:8000/ws/worker/test-worker-001
```

Kirim register message:
```json
{"type": "register", "specs": {"worker_id": "test-worker-001", "os": "Windows"}}
```

Expected: Orchestrator log menampilkan `✅ Worker 'test-worker-001' connected.`

---

## Test 3: End-to-End via Python Script

Simpan sebagai `docs/test_e2e.py` dan jalankan setelah Sprint 1D selesai:

```python
"""
Test end-to-end: Kirim prompt ke Orchestrator → Worker proses → Hasil kembali.
Jalankan: python docs/test_e2e.py
"""

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
        print(f"   TTFT estimasi: {elapsed:.2f}s")


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
```

---

## Test 4: Ukur KPI Fase 1

Script untuk mengukur KPI sesuai ROADMAP:

```python
"""
KPI Measurement Script — Fase 1
Ukur: TTFT, TPS, Memory
"""
import asyncio
import time
import httpx
import psutil
import os


async def measure_ttft(prompt: str, ollama_url: str, model: str) -> float:
    """Time To First Token — waktu hingga token pertama muncul."""
    url = f"{ollama_url}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": True}

    start = time.monotonic()
    first_token_time = None

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, json=payload) as resp:
            async for line in resp.aiter_lines():
                if line:
                    import json
                    chunk = json.loads(line)
                    if chunk.get("response") and first_token_time is None:
                        first_token_time = time.monotonic() - start
                    if chunk.get("done"):
                        break

    return first_token_time or 0.0


def measure_memory_mb() -> float:
    """RAM yang dipakai proses Python saat ini (MB)."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


async def run_kpi_test():
    OLLAMA_URL = "http://localhost:11434"
    MODEL = "llama3.2:3b"
    TEST_PROMPT = "Jelaskan strategi konten untuk kreator teknologi di Indonesia dalam 3 poin."

    print("📊 Mengukur KPI Fase 1...")

    # TTFT
    ttft = await measure_ttft(TEST_PROMPT, OLLAMA_URL, MODEL)
    ttft_status = "✅" if ttft < 1.5 else "❌"
    print(f"{ttft_status} TTFT: {ttft:.2f}s (target: < 1.5s)")

    # Memory
    mem_mb = measure_memory_mb()
    mem_status = "✅" if mem_mb < 4096 else "❌"
    print(f"{mem_status} Memory: {mem_mb:.0f} MB (target: < 4096 MB)")

    print("\nSimpan hasil ini untuk laporan KPI Sprint 1F.")


if __name__ == "__main__":
    asyncio.run(run_kpi_test())
```

Install `psutil` dulu: `pip install psutil`

---

## Checklist QA Fase 1

- [ ] `GET /health` mengembalikan 200 OK
- [ ] Worker berhasil connect & muncul di `/health` response
- [ ] Ping-pong heartbeat berjalan setiap 15 detik
- [ ] Disconnect Worker → hilang dari `/health` response
- [ ] Prompt dikirim → Worker proses → result kembali ke Orchestrator log
- [ ] TTFT < 1.5 detik pada jaringan lokal
- [ ] Memory Worker < 4 GB saat proses inference
- [ ] Worker auto-reconnect saat Orchestrator restart
