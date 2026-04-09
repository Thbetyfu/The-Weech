---
name: theweech_master
description: >
  Master skill index untuk project TheWeech AI Mesh. Berisi referensi ke semua
  skill spesifik yang tersedia. Baca file ini PERTAMA sebelum mengerjakan apapun
  di project TheWeech untuk memahami konteks penuh sistem.
---

# TheWeech Master Skill Index

## Daftar Skill yang Tersedia

| Skill File | Fungsi |
|-----------|--------|
| `theweech_architecture.md` | Pemahaman arsitektur penuh AI Mesh (Orchestrator, Worker, Vault) |
| `python_fastapi_ws.md` | Pattern FastAPI + WebSocket untuk Orchestrator |
| `ollama_integration.md` | Integrasi Ollama lokal — inference, model pull, error handling |
| `sprint_executor.md` | Cara mengeksekusi Sprint dengan benar di project ini |
| `sqlite_sqlalchemy.md` | Pattern SQLAlchemy async + SQLite untuk database lokal |
| `testing_strategy.md` | Strategi QA & testing setiap komponen |

## Konteks Project

- **Nama:** TheWeech AI Mesh
- **Stack Fase 1:** Python 3.12, FastAPI, WebSockets, SQLite (aiosqlite), Ollama
- **Root Directory:** `d:\0. Kerjaan\TheWeech\`
- **Orchestrator Port:** 8000
- **Ollama Port:** 11434

## Aturan Wajib Sebelum Coding

1. SELALU baca `theweech_architecture.md` untuk memahami konteks sistem
2. SELALU cek struktur folder aktual dengan `list_dir` sebelum buat file baru
3. JANGAN duplikasi fungsi — cek apakah sudah ada di `core/` dulu
4. JANGAN buat file di luar struktur yang sudah ada tanpa diskusi
5. SELALU gunakan async/await untuk semua operasi I/O

## 🛡️ Aturan WAJIB: Defensive Programming & Self-Documenting Code

Mulai Fase 2 dan seterusnya, setiap baris kode yang ditulis **WAJIB** mematuhi standar *Enterprise-Grade* berikut, tanpa pengecualian:

1. **Inline Documentation (Penjelasan Kode):**
   Setiap fungsi, class, dan blok logika kompleks wajib diberi *Docstring* atau komentar yang menjelaskan:
   - Apa kegunaan kode ini?
   - Mengapa ditulis dengan cara ini? (Untuk referensi pengembangan berikutnya)
   
   *Contoh:* `# Dibuat menggunakan Lock() agar tidak terjadi race condition saat ratusan Worker terkoneksi bersamaan.`

2. **Preconditions & Assertions:**
   Jangan berasumsi bahwa input yang masuk selalu benar. **Wajib** memvalidasi tipe data, format, dan batasan batas memori (boundary checks) di awal fungsi.
   - Gunakan `if not data: raise ValueError("Data tidak boleh kosong")` sebelum memproses.

3. **Robust Error Handling (Anti-Crash):**
   Setiap operasi berisiko tinggi (e.g. WebSocket, Database I/O, File System) **WAJIB** diapit dengan blok `try-except` spesifik.
   - Jangan pernah menulis `except Exception as e: pass` (Silent fail). Selalu gunakan logger (`logger.error(...)`) dan kembalikan state program kembali aman (Graceful Fallback).
   - Pastikan variabel dibersihkan di blok `finally:`.
