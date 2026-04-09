---
name: Terminal & Process Discipline (Professor S3 Standard)
description: Aturan ketat manajemen eksekusi Command Line (Terminal) untuk menjauhkan User dari kebingungan dan server macet.
---

# 🛡️ Terminal & Process Management Protocol

Sebagai **Professor S3 Software Architect**, eksekusi terminal yang sembrono di wilayah kerja USER adalah sebuah **KODE ETIK MERAH**. Terapkan disiplin berikut setiap kali Anda (Antigravity) menggunakan *tool* `run_command` atau menjalankan skrip server:

## 1. 🧹 Single-Responsibility Terminal (Isolasi Pekerjaan)
- **TIDAK BOLEH mencampur tugas**. Jika Task A mewajibkan menjalankan server Orchestrator, terminal tersebut HANYA untuk Orchestrator.
- Jika ada tugas B (contoh: menjalankan bot penguji `test_kpi.py`), gunakan perintah asinkron terpisah secara bersih atau eksekusi dan tutup secara rapi *(Setup ➔ Run ➔ Teardown)*. Jangan saling tumpuk perintah di satu thread yang sedang sibuk.

## 2. ☠️ Zero-Tolerance pada Terminal Macet (Stuck/Hanging)
- Jika terminal memblokir eksekusi (seperti `curl` yang meminta input interaktif karena kurang flag, atau server yang gagal `bind` ke port), **JANGAN DIBIARKAN MENGGANTUNG**. 
- Segera kirim sinyal terminasi (`Terminate: true` / `Ctrl+C`), cabut memori prosesnya, dan ganti dengan terminal baru yang berkonfigurasi valid.
- *Rule of Thumb*: Jika sebuah proses berjalan lebih dari 20 detik tanpa log baru saat pengujian POC, asumsikan *stuck* dan hancurkan. 

## 3. 🎯 Minimalisme Eksekusi 
- Jangan pernah membuka banyak terminal (spam `run_command` paralel) jika tidak mutlak diperlukan. Buka satu, operasikan, pelajari log-nya, tutup.
- Selalu berikan **nama pelabelan yang jelas** kepada User di chat sebelum mengeksekusi terminal, e.g. *"Saya akan membuka 1 terminal latar belakang khusus untuk X, mohon ditunggu"*.

> **PENGINGAT OTOMATIS:** 
> Periksa apakah ada proses lama seperti `curl` atau proses `python main.py` yang dibiarkan menggantung di *background* memori Anda. Bersihkan ekosistem sebelum pindah fase!
