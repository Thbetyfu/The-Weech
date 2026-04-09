---
description: Setup environment dan jalankan Worker Node TheWeech (requires Orchestrator aktif)
---

# Workflow: Setup & Jalankan Worker Node

## Prerequisites
- Orchestrator sudah berjalan di `http://localhost:8000`
- Ollama sudah terinstall dan berjalan
- Model sudah di-pull: `ollama pull llama3.2:3b`

## Langkah-langkah

1. Buka terminal BARU (jangan matikan terminal Orchestrator)

2. Masuk ke folder worker-node
```powershell
cd "d:\0. Kerjaan\TheWeech\worker-node"
```

3. Buat virtual environment
```powershell
python -m venv .venv
```

4. Aktifkan virtual environment
```powershell
.venv\Scripts\activate
```

5. Install semua dependencies
```powershell
pip install -r requirements.txt
```

6. Salin file konfigurasi
```powershell
copy .env.example .env
```

7. (Opsional) Edit `.env` — ubah `OLLAMA_MODEL` jika ingin pakai model berbeda

// turbo
8. Jalankan Worker
```powershell
python worker.py
```

## Verifikasi Berhasil

Worker berhasil connect jika terminal menampilkan:
```
==================================================
  TheWeech Worker Node
  ID     : worker-a3f2b1c9
  Model  : llama3.2:3b
  Target : ws://localhost:8000/ws/worker
==================================================
✅ Connected as 'worker-a3f2b1c9'
```

Dan di terminal Orchestrator muncul:
```
✅ Worker 'worker-a3f2b1c9' connected. Total: 1
```

Cek di health endpoint — worker harus muncul:
```
GET http://localhost:8000/health
```

## Jalankan Multiple Worker (Simulasi Jaringan)

Buka terminal baru lagi, aktifkan venv, dan jalankan:
```powershell
# Edit .env dulu, ubah WORKER_ID ke nilai berbeda
# Atau set langsung via environment variable:
$env:WORKER_ID="worker-002"; python worker.py
```

## Troubleshooting

| Error | Solusi |
|-------|--------|
| `ConnectionRefusedError` | Orchestrator belum jalan. Jalankan dulu via `run-orchestrator` workflow |
| `Model not found` | Jalankan `ollama pull llama3.2:3b` |
| `Ollama tidak berjalan` | Buka aplikasi Ollama atau `ollama serve` di terminal baru |
| Worker terus reconnect loop | Cek URL di `.env` — pastikan `ORCHESTRATOR_WS_URL=ws://localhost:8000/ws/worker` |
