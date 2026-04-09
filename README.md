# TheWeech AI Mesh

> Decentralized Physical Infrastructure Network (DePIN) untuk kreator konten lokal Indonesia.

## Struktur Project

```
TheWeech/
├── orchestrator/       ← Pusat komando (FastAPI + WebSocket)
│   ├── core/           ← Config, Database, Connection Manager
│   ├── routes/         ← WebSocket & REST API endpoints
│   ├── models/         ← SQLAlchemy models
│   └── main.py         ← Entry point
├── worker-node/        ← Aplikasi Worker komunitas (Python)
│   ├── core/           ← Engine inferensi & utilitas
│   ├── engine/         ← Integrasi Ollama
│   └── worker.py       ← Entry point
├── vault/              ← Data Sanitization Pipeline (NER/masking)
├── web-dashboard/      ← Frontend SaaS TheWeech
├── docs/               ← Dokumentasi teknis
└── ROADMAP.MD          ← Peta jalan pengembangan
```

## Fase Saat Ini: Fase 1 — PoC Lokal

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com) terinstal dan berjalan
- Model sudah di-pull: `ollama pull llama3.2:3b`

---

## Setup & Jalankan

### 1. Orchestrator

```powershell
cd orchestrator

# Buat virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy config
copy .env.example .env

# Jalankan
python main.py
```

Orchestrator berjalan di: `http://localhost:8000`
Health check: `http://localhost:8000/health`

---

### 2. Worker Node

Buka terminal baru:

```powershell
cd worker-node

# Buat virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy config
copy .env.example .env

# Jalankan
python worker.py
```

Worker akan otomatis konek ke Orchestrator dan siap menerima task.

---

## KPI Target Fase 1

| Metrik | Target |
|--------|--------|
| Time To First Token (TTFT) | < 1,5 detik |
| Tokens Per Second (TPS) | > 8 TPS (CPU), > 20 TPS (GPU) |
| Format Parse Rate | > 95% JSON valid |
| Peak Memory | < 4 GB |
| Failover Recovery | < 500 ms |

---

## Roadmap

Lihat [ROADMAP.MD](./ROADMAP.MD) untuk peta jalan lengkap Fase 1–10.
