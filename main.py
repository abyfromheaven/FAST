import customtkinter as ctk
import sqlite3
from datetime import datetime
from config import db_path
from siswa.rekam_wajah import rekamDataWajahSiswa
from siswa.absensi import absensiWajahSiswa
from guru.rekam_wajah import rekamDataWajahGuru
from guru.absensi import absensiWajahGuru
from siswa.latih_wajah import trainingWajahSiswa
from guru.latih_wajah import trainingWajahGuru

class DashboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FAST - Face Attendance Scan Technology")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Main container frame
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Navigation frame
        self.nav_frame = ctk.CTkFrame(self.container, width=200)
        self.nav_frame.pack(side="left", fill="y", padx=(0, 10), pady=10)
        self.nav_frame.pack_propagate(False)

        # Content frame
        self.content_frame = ctk.CTkFrame(self.container)
        self.content_frame.pack(side="right", fill="both", expand=True, pady=10)

        # Navigation Buttons
        self.btn_dashboard = ctk.CTkButton(self.nav_frame, text="Dashboard", command=self.show_dashboard)
        self.btn_rekam_wajah = ctk.CTkButton(self.nav_frame, text="Rekam Wajah", command=self.show_rekam_wajah)
        self.btn_absensi = ctk.CTkButton(self.nav_frame, text="Absensi", command=self.show_absensi)

        self.btn_dashboard.pack(padx=10, pady=(30,10), fill="x")
        self.btn_rekam_wajah.pack(padx=10, pady=10, fill="x")
        self.btn_absensi.pack(padx=10, pady=10, fill="x")

        # Initialize pages
        self.dashboard_page = DashboardPage(self.content_frame)
        self.rekam_wajah_page = RekamWajahPage(self.content_frame)
        self.absensi_page = AbsensiPage(self.content_frame)

        # Show dashboard by default
        self.show_frame(self.dashboard_page)

    def hide_all_frames(self):
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()

    def show_frame(self, frame):
        self.hide_all_frames()
        frame.pack(fill="both", expand=True)
        if hasattr(frame, "refresh"):
            frame.refresh()

    def show_dashboard(self):
        self.show_frame(self.dashboard_page)

    def show_rekam_wajah(self):
        self.show_frame(self.rekam_wajah_page)

    def show_absensi(self):
        self.show_frame(self.absensi_page)

class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.label_welcome = ctk.CTkLabel(
            self, 
            text="Selamat Datang", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.label_welcome.pack(pady=30)


class RekamWajahPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label_title = ctk.CTkLabel(self, text="Rekam Wajah", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.pack(pady=15)

        # Sub-navigation for Guru and Siswa
        self.sub_nav_frame = ctk.CTkFrame(self)
        self.sub_nav_frame.pack(pady=10)

        self.btn_rekam_siswa = ctk.CTkButton(self.sub_nav_frame, text="Siswa", command=self.show_rekam_siswa)
        self.btn_rekam_guru = ctk.CTkButton(self.sub_nav_frame, text="Guru", command=self.show_rekam_guru)

        self.btn_rekam_siswa.pack(side="left", padx=10)
        self.btn_rekam_guru.pack(side="left", padx=10)

        # Content frame for recording
        self.recording_frame = ctk.CTkFrame(self)
        self.recording_frame.pack(pady=20, fill="both", expand=True)

        # Frame siswa & guru yang sudah termasuk tombol latih model dan input di dalamnya
        self.siswa_frame = ctk.CTkFrame(self.recording_frame)
        self.guru_frame = ctk.CTkFrame(self.recording_frame)

        # --- Isi siswa_frame ---
        ctk.CTkLabel(self.siswa_frame, text="Nama Siswa:").pack(pady=(0, 5))
        self.entry_nama_siswa = ctk.CTkEntry(self.siswa_frame)
        self.entry_nama_siswa.pack(pady=5)

        ctk.CTkLabel(self.siswa_frame, text="Kelas Siswa:").pack(pady=(10, 5))
        self.entry_kelas_siswa = ctk.CTkEntry(self.siswa_frame)
        self.entry_kelas_siswa.pack(pady=5)

        self.siswa_rekam_button = ctk.CTkButton(self.siswa_frame, text="Rekam Wajah Siswa", command=self.on_rekam_wajah_siswa)
        self.siswa_rekam_button.pack(pady=10)

        self.siswa_latih_button = ctk.CTkButton(self.siswa_frame, text="Latih Model Wajah Siswa", command=self.on_latih_wajah_siswa)
        self.siswa_latih_button.pack(pady=10)

        # --- Isi guru_frame ---
        ctk.CTkLabel(self.guru_frame, text="Nama Guru:").pack(pady=(0, 5))
        self.entry_nama_guru = ctk.CTkEntry(self.guru_frame)
        self.entry_nama_guru.pack(pady=5)

        ctk.CTkLabel(self.guru_frame, text="Mata Pelajaran:").pack(pady=(10, 5))
        self.entry_kelas_guru = ctk.CTkEntry(self.guru_frame)
        self.entry_kelas_guru.pack(pady=5)

        self.guru_rekam_button = ctk.CTkButton(self.guru_frame, text="Rekam Wajah Guru", command=self.on_rekam_wajah_guru)
        self.guru_rekam_button.pack(pady=10)

        self.guru_latih_button = ctk.CTkButton(self.guru_frame, text="Latih Model Wajah Guru", command=self.on_latih_wajah_guru)
        self.guru_latih_button.pack(pady=10)

        # Tampilkan frame siswa secara default
        self.show_rekam_siswa()

    def show_rekam_siswa(self):
        self.guru_frame.pack_forget()
        self.siswa_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_rekam_guru(self):
        self.siswa_frame.pack_forget()
        self.guru_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def on_rekam_wajah_siswa(self):
        nama = self.entry_nama_siswa.get().strip()
        kelas = self.entry_kelas_siswa.get().strip()
        if not nama or not kelas:
            print("Nama dan kelas siswa harus diisi!")
            return
        print(f"Mulai rekam wajah siswa: {nama}, kelas: {kelas}")
        rekamDataWajahSiswa(nama, kelas)

    def on_rekam_wajah_guru(self):
        nama = self.entry_nama_guru.get().strip()
        mapel = self.entry_kelas_guru.get().strip()
        if not nama or not mapel:
            print("Nama dan mata pelajaran guru harus diisi!")
            return
        print(f"Mulai rekam wajah guru: {nama}, mapel: {mapel}")
        rekamDataWajahGuru(nama, mapel)

    def on_latih_wajah_siswa(self):
        print("Mulai pelatihan wajah siswa...")
        trainingWajahSiswa()
        print("Pelatihan wajah siswa selesai.")

    def on_latih_wajah_guru(self):
        print("Mulai pelatihan wajah guru...")
        trainingWajahGuru()
        print("Pelatihan wajah guru selesai.")

class AbsensiPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label_title = ctk.CTkLabel(self, text="Absensi", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.pack(pady=15)

        self.sub_nav_frame = ctk.CTkFrame(self)
        self.sub_nav_frame.pack(pady=10)

        self.btn_absensi_siswa = ctk.CTkButton(self.sub_nav_frame, text="Absensi Siswa", command=self.show_absensi_siswa)
        self.btn_absensi_guru = ctk.CTkButton(self.sub_nav_frame, text="Absensi Guru", command=self.show_absensi_guru)

        self.btn_absensi_siswa.pack(side="left", padx=10)
        self.btn_absensi_guru.pack(side="left", padx=10)

        self.absensi_siswa_frame = ctk.CTkFrame(self)
        self.absensi_guru_frame = ctk.CTkFrame(self)

        # Absensi Siswa
        self.absensi_siswa_button = ctk.CTkButton(self.absensi_siswa_frame, text="Mulai Absensi Wajah Siswa", command=self.absensi_wajah_siswa)
        self.absensi_siswa_button.pack(pady=20)

        # Absensi Guru
        self.absensi_guru_button = ctk.CTkButton(self.absensi_guru_frame, text="Mulai Absensi Wajah Guru", command=self.absensi_wajah_guru)
        self.absensi_guru_button.pack(pady=20)

        self.show_absensi_siswa()

    def show_absensi_siswa(self):
        self.absensi_guru_frame.pack_forget()
        self.absensi_siswa_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_absensi_guru(self):
        self.absensi_siswa_frame.pack_forget()
        self.absensi_guru_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def absensi_wajah_siswa(self):
        print("Mulai absensi wajah siswa...")
        absensiWajahSiswa()
        print("Absensi wajah siswa selesai.")

    def absensi_wajah_guru(self):
        print("Mulai absensi wajah guru...")
        absensiWajahGuru()
        print("Absensi wajah guru selesai.")

if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()
