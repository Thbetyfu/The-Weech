---
description: Alur integrasi desain Figma/Image ke dalam kode produksi TheWeech
---

# 🧵 Workflow: /design-stitching

Gunakan workflow ini saat USER memberikan aset desain baru (Fama/Screenshot) untuk diimplementasikan.

## 🏁 Tahapan Eksekusi:

1. **Analisis Visual (The Eye):** Bedah screenshot/desain Figma. Identifikasi struktur layout, palet warna, dan aset gambar yang dibutuhkan.
2. **Setup Asset (Static Layer):**
    - Buat/perbarui file `.css` spesifik di folder `orchestrator/static/css/`.
    - Daftarkan variabel CSS baru jika desain memiliki token warna baru.
3. **Template Splicing (The Skeleton):**
    - Buka file `.html` yang relevan di `orchestrator/templates/`.
    - Implementasikan struktur HTML semantik (Header, Main, Section, Card).
    - Hubungkan dengan file CSS statis yang baru dibuat.
// turbo
4. **Mockup Testing (The Feel):** Jelajahi file HTML menggunakan browser subagent atau render lokal untuk memastikan padding, margin, dan alignment sudah presisi dengan desain asli.
5. **Logic Binding:**
    - Sambungkan ID elemen HTML dengan skrip JavaScript di `orchestrator/static/js/`.
    - Pastikan data dinamis dari backend (Jinja2) terisi dengan benar.
6. **Final Polish:** Tambahkan micro-animations (framer-motion style) dan lapor status "Desain Berhasil Dijahit" ke USER.

## 🚩 Aturan Khusus:
- JANGAN menulis CSS di dalam file HTML.
- SELALU gunakan path absolut untuk aset statis (`/static/css/...`).
- PASTIKAN desain bersifat responsif secara default.
