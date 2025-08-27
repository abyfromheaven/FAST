# FAST - Face Attendance Scan Technology

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**FAST (Face Attendance Scan Technology)** adalah aplikasi absensi desktop modern yang memanfaatkan teknologi pengenalan wajah. Dibangun dengan Python dan CustomTkinter, aplikasi ini menyediakan solusi yang efisien dan terstruktur untuk mencatat kehadiran siswa dan guru.

---

### ✨ Fitur Utama

- **Manajemen User Terpisah**: Sistem dapat mengelola data untuk **Siswa** dan **Guru** secara terpisah, termasuk data kelas untuk siswa dan mata pelajaran untuk guru.
- **Registrasi Wajah Cerdas**: Proses pendaftaran wajah yang mudah dengan **ID Wajah (Face ID) yang dibuat secara otomatis** dan acak untuk memastikan keunikan.
- **Absensi Real-time**: Melakukan absensi secara langsung melalui kamera dengan menampilkan nama pengguna yang dikenali.
- **Database Terstruktur**: Menggunakan SQLite dengan skema yang dinormalisasi (4 tabel) untuk menyimpan data user dan catatan kehadiran secara terpisah dan rapi.
- **Antarmuka Modern**: GUI yang bersih dan intuitif dibangun menggunakan library CustomTkinter.
- **Logging Proses**: Semua aktivitas penting seperti registrasi, training, dan error dicatat di terminal untuk kemudahan debugging.

---

### 🛠️ Teknologi yang Digunakan

- **Python 3.10+**
- **OpenCV-Python**: Untuk semua proses pengolahan gambar dan pengenalan wajah (LBPH).
- **CustomTkinter**: Untuk membangun antarmuka pengguna (GUI) yang modern.
- **Pillow (PIL)**: Untuk manipulasi gambar saat proses training.
- **SQLite3**: Sebagai database file-based yang ringan dan portabel.

---

### 🚀 Instalasi & Penggunaan

Untuk menjalankan proyek ini dari source code, ikuti langkah-langkah berikut:

**1. Persiapan Awal**
   - Pastikan Anda memiliki **Python 3.10** atau versi lebih baru.
   - Pastikan **Git** terinstal di sistem Anda.
   - Siapkan sebuah webcam yang berfungsi.

**2. Clone Repository**
   ```bash
   git clone https://github.com/abyfromheaven/FAST.git
   cd FAST
   ```

**3. Instalasi Dependensi**
   Sangat disarankan untuk menggunakan virtual environment.
   ```bash
   # Buat virtual environment (opsional tapi direkomendasikan)
   python -m venv abyenv

   # Linux / macOS
   source abyenv/bin/activate

   # Install semua library yang dibutuhkan
   pip install -r requirements.txt
   ```

**4. Jalankan Aplikasi**
   Setelah semua dependensi terinstal, jalankan file `main.py`.
   ```bash
   python main.py
   ```
   Aplikasi akan terbuka, dan jika ini adalah kali pertama, file database `data/facesentry.db` akan dibuat secara otomatis.

---

### 📂 Struktur Proyek

Struktur direktori telah dirapikan untuk kemudahan pemeliharaan:

```
FAST/
│
├── main.py                # Titik masuk utama aplikasi dan logika GUI
├── config.py              # File konfigurasi terpusat (path, dll.)
├── requirements.txt       # Daftar dependensi Python
├── README.md              # Anda sedang membacanya
│
├── services/              # Folder untuk semua logika inti
│   ├── database_service.py  # Mengelola semua interaksi database
│   └── face_service.py      # Mengelola rekam wajah, training, dan absensi
│
├── data/
│   ├── facesentry.db        # File database SQLite
│   └── datasets/            # Tempat menyimpan gambar wajah hasil registrasi
│       ├── guru/
│       └── siswa/
│
└─── media/                 # Aset media seperti video atau gambar
```

---

### 🧑‍💼 Kontributor Proyek

- **Muhammad Abiyan Hafidz (Aby)** - Application Developer
- **Darwin Baratha** - Web Developer
- **Rekan Aska Rastia** - Dokumentasi & User Support
- **Muhammad Phasa** - Quality Assurance & Project Management

---

### 📄 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE) © 2025 AbyFromHeaven.
