# 🎨 Skill: UI/UX Mastery - TheWeech Edition

## 🛠️ Overview
Skill ini memberikan kemampuan bagi Antigravity untuk menerjemahkan desain Figma/Mockup menjadi kode antarmuka premium dengan fokus pada **Visual Excellence**, **Glassmorphism**, dan **Micro-interactions**.

## 💎 Design Principles (The Weech Standard)
1. **Glassmorphism Core:**
   - Gunakan `backdrop-filter: blur(12px)`.
   - Gunakan `background: rgba(255, 255, 255, 0.03)` untuk panel gelap.
   - Border tipis `1px solid rgba(255, 255, 255, 0.1)` untuk efek kedalaman.
2. **Typography:**
   - Header/Brand: **Outfit** (800 weight untuk judul).
   - Body/Data: **Inter** (400-500 weight).
3. **Color Palette (HSL Curated):**
   - Base BG: `hsl(230, 25%, 8%)`
   - Primary: `hsl(265, 89%, 60%)` (Purple Glow)
   - Success: `hsl(150, 70%, 50%)` (Emerald)
   - Accent: `hsl(315, 85%, 60%)` (Magenta/Pink)

## 🏗️ Technical Implementation
1. **Utility-First CSS:** Gunakan variabel CSS (`:root`) untuk semua token warna.
2. **Modular Templates:** Pisahkan bagian berulang (Navbar, Sidebar) ke dalam folder `templates/shared/`.
3. **Responsive Design:** Wajib menggunakan Grid/Flexbox dengan *Breakpoints* (Mobile: 768px, Tablet: 1024px).
4. **State Management UI:** Setiap tombol harus punya efek `:hover` dan `:active`. Gunakan `transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1)`.

## 🧪 Quality Check (Visual Audit)
- [ ] Apakah desain sudah terasa "hidup" dengan gradien radial?
- [ ] Apakah kontras teks sudah memenuhi standar aksesibilitas?
- [ ] Apakah semua interaksi (klik/hover) sudah memiliki feedback visual?
- [ ] Apakah aset statis (CSS/JS) sudah terpisah dari HTML?
