# 🌐 TheWeech AI Mesh

> **Decentralized Physical Infrastructure Network (DePIN) & Compute-to-Earn Ecosystem** khusus dirancang untuk Kreator Konten dan Agensi Lokal Indonesia.

TheWeech mentransformasi ratusan PC/Laptop menganggur milik komunitas menjadi satu superkomputer terdistribusi untuk melayani *Artificial Intelligence* tanpa mengandalkan korporasi server luar negeri.

---

## 💡 1. Ide Konsep
**TheWeech** adalah kombinasi dari **SaaS (Software as a Service)** untuk Solopreneur/Kreator dan **Grid Komputasi Terdesentralisasi**. 

Alih-alih membayar biaya API LLM *(seperti OpenAI/Anthropic)* yang mahal secara sentral, perangkat lunak ini mendelegasikan tugas analisis teks AI kepada komputer-komputer rumahan relawan (*Worker Nodes*). Sebagai gantinya, relawan mendapatkan kompensasi berupa **Kredit Komputasi** (Compute-to-Earn) yang bisa ditukarkan dengan akun Pro Premium TheWeech tanpa harus membayar sepeser Rupiah pun.

## 🎯 2. Masalah yang Ingin Diselesaikan
1. **Membengkaknya HPP (Cost of Goods Sold):** Start-up AI sering gulung tikar akibat biaya token server cloud (OpenAI/Claude) yang sangat mahal. TheWeech memangkas ongkos ini hingga 70% dengan melempar tugas ke jaringan PC relawan.
2. **Kekhawatiran Kebocoran Privasi (Zero-Trust):** Kreator tidak ingin rahasia riset pasar mereka dibaca oleh pihak ketiga. TheWeech menyelesaikan ini dengan pipa **"The Vault"** — semua nama orang, tempat, dan entitas sensitif akan "di-sensor" secara algoritmik sebelum dikirim ke komputer relawan komunitas.
3. **Monetisasi Hardware Pasif:** Jutaan PC gaming/laptop di Indonesia menyala tanpa tugas berat saat pengguna sedang mengetik/browsing. TheWeech mengutilisasi *idle CPU/GPU* ini menjadi mesin pencetak uang/akun Pro bagi pemiliknya.

## 🛠️ 3. Tech Stack
- **Pusat Komando (Orchestrator):** Python 3.12, FastAPI, Uvicorn, WebSockets.
- **Node Pekerja (Worker Engine):** Python, `psutil` (Telemetry), Ollama API lokal (Gemma/Llama3).
- **Keamanan Data (The Vault):** Algoritma *Named Entity Recognition* (NER) dengan SpaCy (`id_core_news_sm`).
- **Database & Ledger:** SQLite, SQLAlchemy (Asynchronous).
- **Antarmuka (Frontend):** Vanilla Javascript, HTML5, CSS3 bergaya *Glassmorphism* dan *Premium UI*.

## 📂 4. Struktur Project
```text
TheWeech/
├── orchestrator/           ← Pusat Komando SaaS & Load Balancer
│   ├── core/               ← Jantung Arsitektur:
│   │   ├── cheat_guard.py  # Anti-Spoofing & Hacker Protection
│   │   ├── vault.py        # Data Sanitization (Masking/Unmasking)
│   │   ├── models.py       # Skema Database Ledger AI
│   │   └── connection_manager.py # Smart Routing & Telemetry Worker
│   ├── routes/             
│   │   ├── wallet.py       # API Sistem Gamifikasi & Billing
│   │   ├── worker_ws.py    # Tunnel Komunikasi WebSocket P2P
│   │   └── b2b_agency.py   # Eksekutif API MCN & Radar Matchmaking
│   └── templates/          # Frontend Dashboard (HTML/JS)
├── worker-node/            ← Klien Desktop untuk Relawan Komunitas
│   └── worker.py           # Menjalankan Ollama & Melapor Status Hardware
├── docs/                   ← Script Uji Coba Militer (QA)
│   ├── test_e2e.py         # End-to-end load dispatcher
│   └── test_failover.py    # Uji ketahanan "Zombie Worker" (Kabel cabut)
├── ROADMAP.MD              ← Dokumen Induk Pengembangan (Fase 1-10)
└── README.md               ← File dokumentasi ini
```

## 👥 5. Use Case TheWeech
### A. Klien SaaS (Misal: Manajer Kreator / UMKM)
Klien masuk ke dashboard TheWeech untuk meminta **Analisis User DNA** (menganalisis 500 komentar audiens YouTube mereka). Klien ini tidak tahu menahu soal mesin yang memproses. Di mata mereka, TheWeech dengan cepat menyediakan insight matang dalam antarmuka web modern dengan kecepatan kurang dari hitungan detik.

### B. Relawan Node (Kasta Bronze, Silver, Gold)
Seorang relawan (misal: Rendi) menyalakan script `worker.py` di Laptop *Gaming* miliknya. Laptop Rendi dideteksi memiliki RAM dan CPU tinggi (Kasta Gold). Begitu ada tugas analisis berat dari Klien SaaS, Orchestrator langsung menembakkannya ke laptop Rendi.
Rendi rebahan dan membiarkan layar laptop bekerja, sementara indikator poin TheWeech Wallet-nya terus mendulang puluhan **Kredit Komputasi** secara live, yang besoknya bisa ia *Redeem* (Tukarkan) untuk mencoba fitur-fitur berbayar.

### C. Agensi Perusahaan / MCN (Enterprise Edition)
Sebuah Agensi Manajemen Kreator menyewa server/PC bertenaga tinggi untuk dipasangkan *Enterprise Mode* TheWeech. Semua poin komputasi yang mereka sumbangkan langsung dikonversi otomatis menjadi **Potongan Diskon Lisensi Tahunan**. 
Agensi juga memegang Radar *Matchmaking* via `http://127.0.0.1:8000/agency` untuk mengintai kreator/relawan publik dengan nilai komputasi tertinggi *(Top Contributor)* untuk dijadikan daftar kandidat perekrutan bakat TheWeech!

## 🔄 6. Flow Chart (Alur Arsitektur Resolusi Tinggi)

Arsitektur jaringan syaraf buatan TheWeech dibagi dengan sangat rapi berdasarkan siapa yang menatap layar *(User Persona)*. Berikut adalah peta aliran informasi untuk ketiga kasta pengguna tersebut:

### 🧩 A. Alur Klien SaaS Biasa (Konsumen)
Klien menginginkan kecepatan tanpa friksi. Ia mengetik dari browser, dan TheWeech di belakang layar bekerja keras mendistribusikannya dan menjamin rahasia privasi klien aman.

```mermaid
sequenceDiagram
    autonumber
    actor Client as 🧑‍💻 Klien (Web UI)
    participant Orch as 🧠 Orchestrator
    participant Vault as 🛡️ The Vault (NER Guard)
    participant Mesh as 🌐 AI Mesh Network

    Client->>Orch: Minta Analisa Sentimen Komentar YouTube
    Note over Orch: (Menerima Request HTTP)
    Orch->>Vault: Serahkan teks mentah
    Vault-->>Orch: Teks TERSENSOR (Budi -> [PERSON_1])
    Orch->>Mesh: Routing ke Worker tercepat & idle
    Mesh-->>Orch: Mengembalikan kesimpulan analisa JSON
    Orch->>Vault: De-Masking (Kembalikan data [PERSON_1] ke Budi)
    Orch-->>Client: ⚡ Render UI Premium Glassmorphism (Hasil Instan)
```

### 🧩 B. Alur Relawan Node Kreator (Compute-to-Earn)
Para pemancing kredit komputasi menyalakan perangkat *gaming* / PC mereka. Inilah yang terjadi pada mesin mereka dari awal menyala hingga berhasil menebus diskon pro.

```mermaid
sequenceDiagram
    autonumber
    actor Creator as 💻 Relawan (Worker Node)
    participant CG as 👮 Cheat Guard
    participant DB as 💾 Ledger Database
    participant API as 🏦 Wallet API

    Creator->>CG: Request Koneksi WebSocket (Bawa Token Zero-Trust)
    CG-->>Creator: Token Sah! Mengukur RAM & CPU (Telemetry)
    Note over Creator: Worker dalam status IDLE menunggu tugas
    CG->>Creator: PUSH TUGAS: "Sederhanakan Paragraf ini!"
    Creator->>Creator: Memanggil Local Ollama (Inferensi Hardware)
    Creator-->>CG: Mengirimkan Teks Output AI
    CG->>DB: Konversi Kompleksitas CPU -> Integer (Kredit)
    Note over DB: Worker Buffer += 50 Koin
    Creator->>API: Ajukan Redeem Paket Pro (Rp99.000)
    API->>DB: Cek kecukupan saldo komputasi (Transactional Lock)
    DB-->>API: Saldo Dipotong (Burn)
    API-->>Creator: 🎉 Status Akses Terbuka! Kini jadi Akun Pro.
```

### 🧩 C. Alur Klien B2B Enterprise MCN (Agensi & Skema Diskon)
Agensi tidak bermain di kelas satuan. Mereka menembak ratusan *prompt* sekali tekan, lalu menyalakan server kantor mereka untuk mencetak diskon tagihan Rupiah masal.

```mermaid
sequenceDiagram
    autonumber
    actor MCN as 🏢 Manajer MCN
    participant Dash as 🎛️ B2B Dashboard
    participant EntNode as 💻 Server Kantor MCN (Enterprise Mode)
    participant RBAC as 🔑 RBAC Guard & Ledger

    MCN->>Dash: Upload 50 Profil Talent via Batch Processing
    Dash->>RBAC: Verifikasi API-Key Agensi MCN
    RBAC-->>Dash: Sah (Status Enterprise)
    Dash->>Dash: Sebar 50 Tugas ke Seluruh Mesh Publik
    Note left of EntNode: Server Kantor Bekerja menambang secara terpisah
    EntNode->>RBAC: Menyerahkan Hasil AI via socket berlabel "is_enterprise: true"
    RBAC->>RBAC: Hitung Komputasi -> Salurkan ke Poin Potongan Rupiah Agensi
    MCN->>Dash: Cek /discount-status & /matchmaking
    Dash-->>MCN: Menampilkan: "Diskon Lisensi Anda Rp1.500.000. Ini Top Talent Publik untuk direkrut!"
```

## ⚙️ 7. Setup dan Jalankan (Alpha Testnet)

Lakukan di dua instansi terminal Windows/PowerShell (Makin banyak terminal Worker, Load Balancer semakin pintar).

### Langkah 1: Jalankan Orchestrator (Backend SaaS)
```powershell
# 1. Buka Terminal Pertama
cd "d:\0. Kerjaan\TheWeech\orchestrator"
python -m venv .venv
.venv\Scripts\activate

# Install dependensi
pip install -r requirements.txt
copy .env.example .env

# Jalankan
python main.py
```
> 🌍 Akses UI Premium Dashboard di: `http://127.0.0.1:8000`

### Langkah 2: Jalankan Mesin AI Pekerja (Worker Node)
*Pastikan aplikasi [Ollama](https://ollama.com/) Anda telah di-download dan terinstall secara lokal di PC Anda.*

```powershell
# 2. Buka Terminal Kedua (JANGAN matikan yang pertama)
cd "d:\0. Kerjaan\TheWeech\worker-node"
python -m venv .venv
.venv\Scripts\activate

# Install komponen
pip install -r requirements.txt
copy .env.example .env

# Mode Biasa (Pencetak Koin Pro):
python worker.py

# Mode Enterprise B2B (Diskon Penagihan MCN):
# Pastikan di file .env `ENTERPRISE_MODE=true` dan `AGENCY_API_KEY=KUNCI-ANDA`
python worker.py
```

### Langkah 3: Saksikan Keajaibannya (Fase Pengujian)
Setelah `worker.py` melaporkan *Connected as worker-001*, silakan masuk ke `http://127.0.0.1:8000`. Anda akan melihat:
1. Widget spesifikasi PC Anda.
2. Form Input. Cobalah mengetikkan tugas panjang.
3. Koin/Kredit Komputasi di *Wallet* akan bertambah seiring Task yang berhasil Anda kerjakan via Jaringan Mesh Anda sendiri!
