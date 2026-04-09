---
description: Setup environment dan jalankan Orchestrator TheWeech untuk pertama kali
---

# Workflow: Setup & Jalankan Orchestrator

## Prerequisites
- Python 3.12+ terinstall
- Berada di direktori `d:\0. Kerjaan\TheWeech`

## Langkah-langkah

1. Masuk ke folder orchestrator
```powershell
cd "d:\0. Kerjaan\TheWeech\orchestrator"
```

2. Buat virtual environment
```powershell
python -m venv .venv
```

3. Aktifkan virtual environment
```powershell
.venv\Scripts\activate
```

4. Install semua dependencies
```powershell
pip install -r requirements.txt
```

5. Salin file konfigurasi
```powershell
copy .env.example .env
```

6. (Opsional) Edit `.env` jika perlu ubah port atau model default

// turbo
7. Jalankan Orchestrator
```powershell
python main.py
```

## Verifikasi Berhasil

Orchestrator berhasil jalan jika terminal menampilkan:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ Database initialized
```

Cek health di browser atau curl:
```
http://localhost:8000/health
```

## Troubleshooting

| Error | Solusi |
|-------|--------|
| `ModuleNotFoundError` | Pastikan `.venv` aktif, jalankan `pip install -r requirements.txt` |
| `Address already in use :8000` | Matikan proses di port 8000: `netstat -ano \| findstr :8000` |
| `ImportError: cannot import 'aiosqlite'` | `pip install aiosqlite` |
