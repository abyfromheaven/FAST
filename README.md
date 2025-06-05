# FAST - Face Attendance Scan Technology

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey.svg)

**FAST (Face Attendance Scan Technology)** adalah aplikasi absensi berbasis pengenalan wajah yang dibangun menggunakan Python, OpenCV, dan CustomTkinter. Sistem ini mendukung pendataan wajah siswa/guru, pelatihan model, hingga pencatatan kehadiran secara otomatis dengan antarmuka GUI yang modern. Cocok digunakan di lingkungan sekolah, kampus, atau pelatihan.

---

## 🚀 Fitur Utama

- 🎥 Rekam wajah untuk siswa dan guru
- 🧠 Pelatihan model pengenalan wajah (LBPH)
- 📝 Absensi otomatis berdasarkan deteksi wajah
- 💾 Penyimpanan data ke SQLite
- 📢 Notifikasi suara saat berhasil absen (Text to Speech)
- 🔔 Notifikasi real-time via [ntfy.sh](https://ntfy.sh)
- 🧑‍🎓 Antarmuka GUI modern menggunakan CustomTkinter
- 📂 Backup dan pengelolaan wajah terstruktur
- ⚙️ Support Linux dan Windows (Comming Soon!)

<!-- --- -->

<!-- ## 🖼️ Screenshot

| Menu Utama | Absensi Wajah |
|------------|----------------|
| ![main](docs/screenshot_main.png) | ![absen](docs/screenshot_absen.png) |

> *Letakkan gambar di folder `docs/` dengan nama sesuai atau ubah jalur sesuai penempatan file screenshot Anda.* -->

<!-- --- -->

<!-- ## 📹 Panduan Video

[![Tonton di YouTube](https://img.shields.io/badge/Tonton-Panduan%20Video-red?logo=youtube)](https://youtube.com/your-video-link)

> *Gantilah URL dengan link video demo penggunaan jika sudah tersedia.* -->

---

## 💡 Cara Kerja Sistem

1. User merekam wajah siswa/guru melalui kamera  
2. Sistem menyimpan wajah ke folder & database  
3. User melatih model pengenalan wajah (LBPH)  
4. Saat proses absensi, kamera menangkap wajah  
5. Jika wajah cocok, maka:  
   - ✅ Absensi dicatat otomatis di database  
   - 📢 Suara akan memberi tahu "Absensi Berhasil"  
   - 🔔 Notifikasi dikirim ke `ntfy.sh` (jika aktif)  

---

## 💻 Instalasi dan Penggunaan

### ⚖️ 1. Persiapan

- Pastikan Python 3.9+ terinstal  
- Siapkan webcam  
- Clone repo ini:

```bash
git clone https://github.com/abyfromheaven/FAST.git
cd FAST
📦 1. Install Dependensi
bash
Copy
Edit
pip install -r requirements.txt

🚀 2. Jalankan Aplikasi
bash
Copy
Edit
python main.py
⚙️ Konfigurasi Notifikasi (Opsional)
Buka ntfy.sh

Ganti ntfy_url di main.py ke channel kamu, misalnya:

python
Copy
Edit
ntfy_url = "https://ntfy.sh/absen-xyz"
Buka link tersebut di HP/browser untuk melihat notifikasi absensi.

🏁 Platform yang Didukung
✅ Linux (tested on Ubuntu)

✅ Windows (Coming Soon)

# 📌 Catatan: Untuk Windows, pastikan Python dan kamera sudah berfungsi. Sesuaikan jalur folder jika perlu (datawajah/ dll.)

# 📂 Struktur Folder
# graphql
# Copy
# Edit
# FAST/
# |
# ├── main.py                  # File utama GUI
# ├── datawajah/               # Rekaman wajah per ID
# ├── model/                   # Model LBPH hasil training
# ├── database.db              # Database SQLite absensi
# ├── docs/                    # Gambar screenshot dan dokumentasi
# └── README.md
🔒 Rencana Fitur Selanjutnya
 Login admin & autentikasi

 Dashboard statistik absensi

 Ekspor ke Excel

 Anti-spoofing sederhana

 Versi installer .exe untuk Windows

🤝 Kontribusi
Proyek ini masih berkembang, silakan fork jika ingin membantu atau menambahkan fitur baru.

🧑‍💼 Developer
Muhammad Abiyan Hafidz (Aby)
Pelajar RPL | Cyber Security Enthusiast
GitHub: @abyfromheaven

👥 Kelompok Proyek IPAS
Aplikasi ini merupakan bagian dari Proyek IPAS (Ilmu Pengetahuan Alam dan Sosial) yang dikerjakan secara berkelompok dengan tujuan menggabungkan teknologi dan solusi sosial, khususnya dalam meningkatkan efisiensi sistem absensi di sekolah.

Anggota Kelompok:

👤 Muhammad Abiyan Hafidz – Application Developer
Bertanggung jawab dalam merancang dan membangun sistem utama FAST, termasuk pemrograman Python, database, dan antarmuka pengguna (GUI).

👤 Darwin Baratha – Web Developer
Bertanggung jawab membuat dan mengelola website promosi FAST, UI/UX, termasuk penulisan konten, pengunggahan panduan, dan integrasi dengan GitHub Pages.

👤 Rekan Aska Rastia – Dokumentasi & Support Pengguna
Fokus pada pembuatan dokumentasi manual, panduan penggunaan, dan membantu memastikan dokumentasi mudah dipahami oleh pengguna.

👤 Muhammad Phasa  – Quality Assurance & Testing
Bertugas melakukan uji coba aplikasi, menemukan bug, memberikan umpan balik, memastikan aplikasi berjalan dengan baik dari sisi pengguna umum, memberikan saran, dan memanajemen projek.

📄 License
MIT License © 2025 AbyFromHeaven