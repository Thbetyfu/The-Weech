---
name: sprint_executor
description: >
  Panduan cara Antigravity mengeksekusi Sprint di project TheWeech dengan
  benar. Berisi checklist sebelum coding, aturan naming, cara validasi hasil,
  dan cara melaporkan status ke user.
---

# Sprint Executor Skill

## Definisi Sprint TheWeech

Setiap Sprint = satu unit pekerjaan yang bisa diselesaikan dalam satu sesi.
Format penamaan: `Sprint [Fase][Huruf] — [Deskripsi Singkat]`

Contoh: `Sprint 1C — Buat Orchestrator WebSocket`

---

## Checklist Wajib SEBELUM Menulis Kode

1. **Baca arsitektur** — Baca `.agents/skills/theweech_architecture.md`
2. **Cek struktur folder aktual** — `list_dir` pada direktori yang akan dimodifikasi
3. **Grep fungsi yang sudah ada** — Pastikan tidak ada duplikasi
4. **Konfirmasi dengan user** — Jika ada ambiguitas desain, tanya dulu
5. **Identifikasi file yang akan dibuat/dimodifikasi** — Tulis daftarnya ke user

---

## Urutan Sprint Fase 1

| Sprint | Deskripsi | Status |
|--------|-----------|--------|
| **1A** | Setup struktur folder & file fondasi | ✅ SELESAI |
| **1B** | Verifikasi Ollama + install dependencies | ⏳ Menunggu user |
| **1C** | Jalankan Orchestrator + verifikasi koneksi WebSocket | ⬜ |
| **1D** | Jalankan Worker + test konek ke Orchestrator | ⬜ |
| **1E** | End-to-end test: dispatch prompt → Ollama → result kembali | ⬜ |
| **1F** | Ukur KPI: TTFT, TPS, Memory footprint | ⬜ |

---

## Cara Melaporkan Status Sprint

Setiap Sprint selesai, laporkan ke user dengan format ini:

```
## ✅ Sprint [ID] — SELESAI

### Yang Dikerjakan:
- [file/fitur 1]
- [file/fitur 2]

### Cara Menjalankan:
[perintah terminal yang perlu dijalankan user]

### Hasil yang Diharapkan:
[output yang seharusnya muncul di terminal]

### Langkah Berikutnya (Sprint [ID+1]):
[preview sprint berikutnya]
```

---

## Aturan Naming Konvensi Project TheWeech

| Konteks | Konvensi | Contoh |
|---------|----------|--------|
| File Python | `snake_case.py` | `connection_manager.py` |
| Class Python | `PascalCase` | `ConnectionManager` |
| Function/method | `snake_case` | `get_idle_worker()` |
| Konstanta | `UPPER_SNAKE` | `HEARTBEAT_INTERVAL` |
| Environment var | `UPPER_SNAKE` | `OLLAMA_BASE_URL` |
| WebSocket route | `/ws/[komponen]/[id]` | `/ws/worker/abc123` |
| REST endpoint | `/api/v1/[resource]` | `/api/v1/dispatch` |
| Worker ID | `worker-[hex8]` | `worker-a3f2b1c9` |

---

## Cara Validasi Kode yang Dibuat

Setelah menulis kode, lakukan ini sebelum lapor ke user:

1. **Syntax check** — Pastikan tidak ada SyntaxError visual
2. **Import consistency** — Semua import ada dan path-nya benar
3. **Type hints** — Semua function parameter dan return type ada
4. **Async correctness** — Tidak ada blocking call di dalam `async def`
5. **Error handling** — Tidak ada bare `except:` tanpa logging
6. **No hardcoded secrets** — URL/key dibaca dari `settings` atau `.env`

---

## Ketika Menemui Error

### Error saat install dependencies
```powershell
# Jika pip error, coba upgrade dulu
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Error `ModuleNotFoundError`
- Pastikan virtual environment aktif (ada `.venv\Scripts\activate`)
- Pastikan install dilakukan di dalam folder yang benar

### Error `ConnectionRefusedError` saat Worker connect
- Pastikan Orchestrator sudah jalan dulu
- Cek port 8000 tidak dipakai proses lain: `netstat -ano | findstr :8000`

### Error Ollama `404 Not Found`
- Model belum di-pull: `ollama pull llama3.2:3b`
- Ollama belum jalan: buka aplikasi Ollama atau `ollama serve`

---

## Prioritas Saat Mengerjakan Task

1. **Fungsional dulu** — Kode harus bisa jalan sebelum dioptimasi
2. **Minimal viable** — Jangan over-engineer untuk Fase yang belum tiba
3. **Terstruktur** — Ikuti folder struktur yang sudah ada
4. **Bisa di-extend** — Tulis kode yang mudah ditambah fitur di sprint berikutnya
