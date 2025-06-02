import customtkinter as ctk
import sqlite3
from datetime import datetime
from config import db_path
from siswa.rekam_wajah import rekamDataWajahSiswa
from siswa.absensi import absensiWajahSiswa
from guru.rekam_wajah import rekamDataWajahGuru
from guru.absensi import absensiWajahGuru

class DashboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FaceSentri - Dashboard")
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
        self.label_title = ctk.CTkLabel(self, text="Dashboard Overview", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.pack(pady=15)

        # Overview frames
        self.overview_frame = ctk.CTkFrame(self)
        self.overview_frame.pack(pady=20, padx=20, fill="x")

        # Student attendance summary
        self.label_siswa_title = ctk.CTkLabel(self.overview_frame, text="Absensi Siswa Hari Ini", font=ctk.CTkFont(size=18))
        self.label_siswa_title.grid(row=0, column=0, sticky="w", padx=10, pady=(10,5))
        self.label_siswa_count = ctk.CTkLabel(self.overview_frame, text="Loading...")
        self.label_siswa_count.grid(row=1, column=0, sticky="w", padx=10, pady=(0,15))

        # Teacher attendance summary
        self.label_guru_title = ctk.CTkLabel(self.overview_frame, text="Absensi Guru Hari Ini", font=ctk.CTkFont(size=18))
        self.label_guru_title.grid(row=0, column=1, sticky="w", padx=30, pady=(10,5))
        self.label_guru_count = ctk.CTkLabel(self.overview_frame, text="Loading...")
        self.label_guru_count.grid(row=1, column=1, sticky="w", padx=30, pady=(0,15))

        # Recent Attendance Logs
        self.label_recent_title = ctk.CTkLabel(self, text="Catatan Absensi Terbaru", font=ctk.CTkFont(size=18))
        self.label_recent_title.pack(pady=(20, 10))

        self.recent_frame = ctk.CTkFrame(self)
        self.recent_frame.pack(pady=10, padx=20, fill="x")

        self.recent_logs = ctk.CTkTextbox(self.recent_frame, height=200)
        self.recent_logs.pack(fill="both", expand=True)

        self.refresh_recent_logs()

    def refresh(self):
        # Query attendance counts for today
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            today = datetime.now().strftime("%Y-%m-%d")

            cur.execute("SELECT COUNT(DISTINCT nama) FROM absensi WHERE DATE(waktu) = ?", (today,))
            siswa_count = cur.fetchone()[0] or 0

            cur.execute("SELECT COUNT(DISTINCT nama) FROM absensi_guru WHERE DATE(waktu) = ?", (today,))
            guru_count = cur.fetchone()[0] or 0

            conn.close()
        except Exception as e:
            siswa_count = "Error"
            guru_count = "Error"

        self.label_siswa_count.configure(text=f"Jumlah siswa yang absen hari ini: {siswa_count}")
        self.label_guru_count.configure(text=f"Jumlah guru yang absen hari ini: {guru_count}")

    def refresh_recent_logs(self):
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            # Get recent student attendance
            cur.execute("SELECT nama, kelas, waktu FROM absensi ORDER BY waktu DESC LIMIT 5")
            siswa_logs = cur.fetchall()

            # Get recent teacher attendance
            cur.execute("SELECT nama, mapel, waktu FROM absensi_guru ORDER BY waktu DESC LIMIT 5")
            guru_logs = cur.fetchall()

            conn.close()

            # Clear previous logs
            self.recent_logs.delete("1.0", ctk.END)

            # Display recent logs
            self.recent_logs.insert(ctk.END, "Absensi Siswa:\n")
            for log in siswa_logs:
                self.recent_logs.insert(ctk.END, f"{log[0]} (Kelas: {log[1]}) - {log[2]}\n")

            self.recent_logs.insert(ctk.END, "\nAbsensi Guru:\n")
            for log in guru_logs:
                self.recent_logs.insert(ctk.END, f"{log[0]} (Mata Pelajaran: {log[1]}) - {log[2]}\n")

        except Exception as e:
            self.recent_logs.insert(ctk.END, "Error loading logs.")

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
        self.recording_frame.pack(pady=20)

        self.siswa_frame = SiswaRekamWajahFrame(self.recording_frame)
        self.guru_frame = GuruRekamWajahFrame(self.recording_frame)

        self.show_rekam_siswa()  # Show siswa frame by default

    def show_rekam_siswa(self):
        self.guru_frame.pack_forget()
        self.siswa_frame.pack(fill="both", expand=True)

    def show_rekam_guru(self):
        self.siswa_frame.pack_forget()
        self.guru_frame.pack(fill="both", expand=True)

class AbsensiPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label_title = ctk.CTkLabel(self, text="Absensi", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.pack(pady=15)

        # Sub-navigation for Guru and Siswa
        self.sub_nav_frame = ctk.CTkFrame(self)
        self.sub_nav_frame.pack(pady=10)

        self.btn_absensi_siswa = ctk.CTkButton(self.sub_nav_frame, text="Siswa", command=self.show_absensi_siswa)
        self.btn_absensi_guru = ctk.CTkButton(self.sub_nav_frame, text="Guru", command=self.show_absensi_guru)

        self.btn_absensi_siswa.pack(side="left", padx=10)
        self.btn_absensi_guru.pack(side="left", padx=10)

        # Content frame for attendance
        self.attendance_frame = ctk.CTkFrame(self)
        self.attendance_frame.pack(pady=20)

        self.siswa_absensi_frame = SiswaAbsensiFrame(self.attendance_frame)
        self.guru_absensi_frame = GuruAbsensiFrame(self.attendance_frame)

        self.show_absensi_siswa()  # Show siswa frame by default

    def show_absensi_siswa(self):
        self.guru_absensi_frame.pack_forget()
        self.siswa_absensi_frame.pack(fill="both", expand=True)

    def show_absensi_guru(self):
        self.siswa_absensi_frame.pack_forget()
        self.guru_absensi_frame.pack(fill="both", expand=True)

class SiswaRekamWajahFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        label = ctk.CTkLabel(self, text="Rekam Wajah Siswa", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=20)
        # Inputs for name and class
        self.frame_inputs = ctk.CTkFrame(self)
        self.frame_inputs.pack(pady=10, padx=10)

        ctk.CTkLabel(self.frame_inputs, text="Nama Siswa").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.entry_nama = ctk.CTkEntry(self.frame_inputs)
        self.entry_nama.grid(row=0, column=1, padx=5, pady=10)

        ctk.CTkLabel(self.frame_inputs, text="Kelas").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.entry_kelas = ctk.CTkEntry(self.frame_inputs)
        self.entry_kelas.grid(row=1, column=1, padx=5, pady=10)

        self.btn_rekam = ctk.CTkButton(self.frame_inputs, text="Rekam Wajah", command=self.rekam_wajah)
        self.btn_rekam.grid(row=2, column=0, columnspan=2, pady=20)

    def rekam_wajah(self):
        nama = self.entry_nama.get()
        kelas = self.entry_kelas.get()
        if not nama or not kelas:
            from tkinter import messagebox
            messagebox.showwarning("Peringatan", "Nama dan kelas harus diisi!")
            return
        # Call the existing rekamDataWajahSiswa function with entry widgets
        rekamDataWajahSiswa(self.entry_nama, self.entry_kelas)

    def refresh(self):
        self.entry_nama.delete(0, "end")
        self.entry_kelas.delete(0, "end")

class GuruRekamWajahFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        label = ctk.CTkLabel(self, text="Rekam Wajah Guru", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=20)

        self.frame_inputs = ctk.CTkFrame(self)
        self.frame_inputs.pack(pady=10, padx=10)

        ctk.CTkLabel(self.frame_inputs, text="Nama Guru").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.entry_nama = ctk.CTkEntry(self.frame_inputs)
        self.entry_nama.grid(row=0, column=1, padx=5, pady=10)

        ctk.CTkLabel(self.frame_inputs, text="Mata Pelajaran").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.entry_mapel = ctk.CTkEntry(self.frame_inputs)
        self.entry_mapel.grid(row=1, column=1, padx=5, pady=10)

        self.btn_rekam = ctk.CTkButton(self.frame_inputs, text="Rekam Wajah", command=self.rekam_wajah)
        self.btn_rekam.grid(row=2, column=0, columnspan=2, pady=20)

    def rekam_wajah(self):
        nama = self.entry_nama.get()
        mapel = self.entry_mapel.get()
        if not nama or not mapel:
            from tkinter import messagebox
            messagebox.showwarning("Peringatan", "Nama dan mapel harus diisi!")
            return
        # Call the existing rekamDataWajahGuru function with entry widgets
        rekamDataWajahGuru(self.entry_nama, self.entry_mapel)

    def refresh(self):
        self.entry_nama.delete(0, "end")
        self.entry_mapel.delete(0, "end")

class SiswaAbsensiFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        label = ctk.CTkLabel(self, text="Absensi Wajah Siswa", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=20)

        self.btn_absensi = ctk.CTkButton(self, text="Mulai Absensi Wajah Siswa", command=self.mulai_absensi)
        self.btn_absensi.pack(pady=20)

    def mulai_absensi(self):
        absensiWajahSiswa()

    def refresh(self):
        pass

class GuruAbsensiFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        label = ctk.CTkLabel(self, text="Absensi Wajah Guru", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=20)

        self.btn_absensi = ctk.CTkButton(self, text="Mulai Absensi Wajah Guru", command=self.mulai_absensi)
        self.btn_absensi.pack(pady=20)

    def mulai_absensi(self):
        absensiWajahGuru()

    def refresh(self):
        pass

if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()
