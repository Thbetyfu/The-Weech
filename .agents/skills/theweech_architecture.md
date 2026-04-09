---
name: theweech_architecture
description: >
  Pemahaman penuh arsitektur TheWeech AI Mesh — komponen, alur data, protokol
  komunikasi, dan keputusan desain di setiap fase. Baca skill ini sebelum
  menyentuh kode apapun di project ini.
---

# TheWeech Architecture Skill

## Gambaran Sistem

TheWeech adalah Decentralized Physical Infrastructure Network (DePIN) untuk
kreator konten Indonesia. Laptoppengguna menjadi Worker Node yang memproses
AI inference, dikoordinasi oleh Orchestrator terpusat.

```
[User Browser]
     ↓ REST / WebSocket
[Orchestrator (FastAPI)]  ←→  [Worker Node 1 (Ollama)]
     ↓                         [Worker Node 2 (Ollama)]
[The Vault (NER)]               [Worker Node N (Ollama)]
     ↓
[SQLite / PostgreSQL]
```

---

## Komponen Utama

### 1. Orchestrator (`orchestrator/`)
- **Entry:** `main.py` — FastAPI app dengan lifespan
- **Config:** `core/config.py` — Pydantic Settings, baca `.env`
- **Database:** `core/database.py` — SQLAlchemy async engine
- **Registry Worker:** `core/connection_manager.py` — dict `worker_id → WorkerInfo`
- **WebSocket Route:** `routes/worker_ws.py` — `/ws/worker/{worker_id}`
- **Health Check:** `routes/health.py` — `/health`

### 2. Worker Node (`worker-node/`)
- **Entry:** `worker.py` — asyncio loop, auto-reconnect
- **Inference:** Memanggil Ollama REST API di `localhost:11434`
- **Protokol:** JSON messages via WebSocket

### 3. The Vault (`vault/`) — Fase 2+
- Pipeline NER untuk masking data sensitif sebelum dikirim ke Worker publik
- Belum diimplementasi di Fase 1

### 4. Web Dashboard (`web-dashboard/`) — Fase 2+
- Frontend SaaS TheWeech
- Belum diimplementasi di Fase 1

---

## Protokol Komunikasi WebSocket

Semua pesan adalah JSON. Format standar:

```json
{ "type": "<message_type>", ...payload }
```

### Pesan dari Worker → Orchestrator

| type | Payload | Kapan |
|------|---------|-------|
| `register` | `{ "specs": { "worker_id", "os", "model" } }` | Saat pertama connect |
| `pong` | _(kosong)_ | Membalas `ping` dari Orchestrator |
| `result` | `{ "task_id", "output", "duration_seconds" }` | Setelah selesai inferensi |
| `error` | `{ "task_id", "message" }` | Jika inferensi gagal |

### Pesan dari Orchestrator → Worker

| type | Payload | Kapan |
|------|---------|-------|
| `ping` | _(kosong)_ | Setiap 15 detik (heartbeat) |
| `task` | `{ "task_id", "prompt" }` | Saat ada pekerjaan untuk diproses |

---

## Konvensi Kode

### Wajib dipatuhi:
1. **Semua I/O harus async** — `async def`, `await`, tidak boleh blocking
2. **Type hints** di semua function signature
3. **Logging** dengan `logger = logging.getLogger(__name__)` bukan `print()`
4. **Config** selalu dari `core/config.py` (Settings), bukan hardcode string
5. **Error handling** harus spesifik, bukan `except Exception: pass`

### Struktur file baru:
```python
"""
Penjelasan singkat modul ini.
"""
# imports stdlib
# imports third-party
# imports internal (relative)
# constants
# classes/functions
```

---

## Status Per Fase

| Fase | Status | Komponen yang Dibangun |
|------|--------|----------------------|
| **Fase 1** | 🟡 In Progress | Orchestrator (WebSocket + Health), Worker (Ollama + auto-reconnect) |
| Fase 2 | ⬜ Belum | The Vault (NER), Deploy ke cloud, Heartbeat hardening |
| Fase 3 | ⬜ Belum | Smart Routing, Ledger Compute-to-Earn |
| Fase 4–10 | ⬜ Belum | Lihat ROADMAP.MD |

---

## Keputusan Desain Penting

### Mengapa SQLite di Fase 1?
Zero-config, tidak perlu install server DB. Di Fase 2+ akan migrasi ke PostgreSQL
dengan mengubah `DATABASE_URL` di `.env` saja — karena kita pakai SQLAlchemy ORM.

### Mengapa Ollama bukan llama.cpp langsung?
Ollama membungkus llama.cpp dengan REST API yang stabil dan cross-platform.
User tidak perlu install CUDA/driver manual. Di Fase 6 kita bisa extend dengan
model fine-tuned Weech-Nusantara.

### Mengapa WebSocket bukan gRPC untuk Fase 1?
WebSocket lebih mudah di-debug (bisa pakai browser), library tersedia di semua
platform, dan cukup untuk PoC. gRPC dapat dipertimbangkan di Fase 5+ untuk
throughput B2B enterprise.
