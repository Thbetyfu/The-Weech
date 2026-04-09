---
description: Eksekusi Sprint baru di project TheWeech — mulai dari cek konteks hingga lapor ke user
---

# Workflow: Eksekusi Sprint

## Langkah-langkah

1. Baca skill arsitektur sebelum memulai
```
Baca file: d:\0. Kerjaan\TheWeech\.agents\skills\theweech_architecture.md
Baca file: d:\0. Kerjaan\TheWeech\.agents\skills\sprint_executor.md
```

2. Cek status sprint terakhir
```
Tanya user: "Sprint sebelumnya sudah selesai? Ada error yang perlu diselesaikan dulu?"
```

3. Identifikasi sprint yang akan dikerjakan dari tabel di sprint_executor.md

4. Lakukan context research
```powershell
# Lihat struktur folder terbaru
Get-ChildItem -Recurse "d:\0. Kerjaan\TheWeech" -Exclude ".venv","__pycache__" | Where-Object { !$_.PSIsContainer } | Select-Object FullName
```

5. Grep untuk cek duplikasi sebelum buat file baru
```powershell
# Contoh: cek apakah fungsi sudah ada
Select-String -Path "d:\0. Kerjaan\TheWeech\orchestrator\**\*.py" -Pattern "def nama_fungsi"
```

6. Konfirmasikan rencana ke user sebelum mulai coding
```
Lapor: "Sprint [ID] — saya akan mengerjakan [deskripsi]. File yang akan dibuat/dimodifikasi: [list]. Boleh mulai?"
```

7. Eksekusi coding sesuai skill yang relevan dan **WAJIB MENERAPKAN DEFENSIVE PROGRAMMING**:
```
- Dokumentasi Inline: Tambahkan komentar yang menjelaskan ALASAN DIBUATNYA KODE (apa tujuannya untuk pengembangan tahap selanjutnya).
- Preconditions: Wajib tervalidasi sebelum logic dieksekusi (e.g. validasi struktur JSON, data kosong, dll).
- Error Handling: Gunakan try-except spesifik, jangan pernah silent exception. Pastikan state program tetap stabil setelah exception.
```

8. Validasi kode (lihat checklist di sprint_executor.md)
```
- Cek ulang apakah ada variabel yang tidak tertutup di block 'finally:'
- Pastikan tidak ada asumsi buta terhadap input klien
```

// turbo
9. Lakukan verifikasi struktur file yang dibuat
```powershell
Get-ChildItem "d:\0. Kerjaan\TheWeech" -Recurse -Filter "*.py" | Select-Object FullName
```

10. Lapor hasil ke user dengan format standar dari sprint_executor.md
