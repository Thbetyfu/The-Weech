---
description: Jalankan test end-to-end dan ukur KPI Fase 1 TheWeech
---

# Workflow: Test End-to-End & Ukur KPI

## Prerequisites
- Orchestrator berjalan di port 8000
- Minimal 1 Worker Node aktif dan terkoneksi
- Ollama berjalan dengan model yang sudah di-pull

## Langkah-langkah

1. Pastikan semua service berjalan
```powershell
curl http://localhost:8000/health
```
Response harus menunjukkan `"active_workers": 1` atau lebih.

2. Masuk ke folder docs
```powershell
cd "d:\0. Kerjaan\TheWeech"
```

3. Aktifkan venv worker (untuk akses httpx)
```powershell
.\worker-node\.venv\Scripts\activate
```

4. Install psutil untuk pengukuran memory
```powershell
pip install psutil
```

// turbo
5. Jalankan test end-to-end
```powershell
python docs\test_e2e.py
```

6. Jalankan KPI measurement
```powershell
python docs\kpi_measure.py
```

## Interpretasi Hasil KPI

| Metrik | Target | Jika Tidak Tercapai |
|--------|--------|---------------------|
| TTFT < 1.5s | Jaringan lokal | Coba model lebih kecil: `llama3.2:1b` |
| TPS > 8 (CPU) | CPU-only inference | Normal — catat sebagai baseline |
| Memory < 4GB | Worker saat inferensi | Kurangi `num_predict` di payload |
| Fallback < 500ms | Matikan Worker paksa | Cek log Orchestrator |

## Cara Simulasi Failover (Sprint 1F)

1. Jalankan 2 Worker di terminal berbeda
2. Pastikan keduanya muncul di `/health`
3. Matikan paksa Worker pertama (Ctrl+C)
4. Ukur berapa lama hingga Worker hilang dari `/health`
5. Catat waktu — harus < 500ms (tergantung heartbeat interval)
