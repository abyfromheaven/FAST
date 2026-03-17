import customtkinter as ctk
from tkinter import messagebox
import threading
import random

# Impor dari file lokal
import config
from services.database_service import DatabaseService
from services.face_service import FaceService

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FAST - Face Attendance Scan Technology")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Inisialisasi Service
        try:
            self.db_service = DatabaseService(config.DATABASE_PATH)
            self.face_service = FaceService(self.db_service)
        except FileNotFoundError as e:
            messagebox.showerror("Error Kritis", f"Gagal memulai aplikasi: {e}")
            self.after(100, self.destroy)
            return

        # --- UI Setup ---
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.nav_frame = ctk.CTkFrame(self.container, width=200)
        self.nav_frame.pack(side="left", fill="y", padx=(0, 10), pady=10)
        self.nav_frame.pack_propagate(False)

        self.content_frame = ctk.CTkFrame(self.container)
        self.content_frame.pack(side="right", fill="both", expand=True, pady=10)

        self.btn_dashboard = ctk.CTkButton(self.nav_frame, text="Dashboard", command=self.show_dashboard)
        self.btn_rekam_wajah = ctk.CTkButton(self.nav_frame, text="Rekam & Latih", command=self.show_rekam_wajah)
        self.btn_absensi = ctk.CTkButton(self.nav_frame, text="Absensi", command=self.show_absensi)

        self.btn_dashboard.pack(padx=10, pady=(30,10), fill="x")
        self.btn_rekam_wajah.pack(padx=10, pady=10, fill="x")
        self.btn_absensi.pack(padx=10, pady=10, fill="x")

        # Inisialisasi semua halaman (frames)
        self.pages = {
            "dashboard": DashboardPage(self.content_frame),
            "rekam": RekamWajahPage(self.content_frame, self.face_service),
            "absensi": AbsensiPage(self.content_frame, self.face_service)
        }

        self.show_frame("dashboard")

    def show_frame(self, page_name):
        for page in self.pages.values():
            page.pack_forget()
        
        frame = self.pages[page_name]
        frame.pack(fill="both", expand=True)

    def show_dashboard(self): self.show_frame("dashboard")
    def show_rekam_wajah(self): self.show_frame("rekam")
    def show_absensi(self): self.show_frame("absensi")

class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text="Selamat Datang di FAST", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=30)
        ctk.CTkLabel(self, text="Pilih menu di samping untuk memulai.", font=ctk.CTkFont(size=16)).pack(pady=10)

class RekamWajahPage(ctk.CTkFrame):
    def __init__(self, parent, face_service):
        super().__init__(parent)
        self.face_service = face_service
        # Dapatkan db_service dari parent utama (App)
        self.db_service = parent.master.master.db_service

        ctk.CTkLabel(self, text="Registrasi & Training", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=15, anchor="w", padx=20)

        # --- Form Input ---
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(pady=10, padx=20, fill="x")

        self.user_type_var = ctk.StringVar(value="siswa")
        self.user_type_var.trace_add("write", self._update_form)

        ctk.CTkLabel(form_frame, text="Tipe Pengguna:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkRadioButton(form_frame, text="Siswa", variable=self.user_type_var, value="siswa").grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkRadioButton(form_frame, text="Guru", variable=self.user_type_var, value="guru").grid(row=0, column=2, padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="Nama Lengkap:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_nama = ctk.CTkEntry(form_frame, placeholder_text="Contoh: Abiyan")
        self.entry_nama.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        self.label_extra = ctk.CTkLabel(form_frame, text="Kelas:")
        self.label_extra.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.entry_extra = ctk.CTkEntry(form_frame, placeholder_text="Contoh: XI RPL")
        self.entry_extra.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        # --- Tombol Aksi ---
        action_frame = ctk.CTkFrame(self)
        action_frame.pack(pady=20, padx=20, fill="x")

        self.rekam_button = ctk.CTkButton(action_frame, text="1. Mulai Perekaman Wajah", command=self.handle_rekam)
        self.rekam_button.pack(pady=10, fill="x")

        self.latih_button = ctk.CTkButton(action_frame, text="2. Latih Model (Global)", command=self.handle_latih)
        self.latih_button.pack(pady=10, fill="x")

        # --- Status Label ---
        self.status_label = ctk.CTkLabel(self, text="Status: Siap", font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=10, padx=20, anchor="w")

        self._update_form() # Panggil sekali saat inisialisasi

    def _update_form(self, *args):
        """Mengubah label dan placeholder berdasarkan tipe user."""
        user_type = self.user_type_var.get()
        if user_type == 'siswa':
            self.label_extra.configure(text="Kelas:")
            self.entry_extra.configure(placeholder_text="Contoh: XI RPL")
        else: # guru
            self.label_extra.configure(text="Mata Pelajaran:")
            self.entry_extra.configure(placeholder_text="Contoh: Pemrograman Dasar")

    def handle_rekam(self):
        user_type = self.user_type_var.get()
        nama = self.entry_nama.get().strip()
        extra_data = self.entry_extra.get().strip()

        # 1. Validasi Input
        if not nama or not extra_data:
            messagebox.showwarning("Input Tidak Lengkap", "Harap isi semua field yang tersedia.")
            return

        # 2. Generate Face ID Unik
        self.status_label.configure(text="Status: Menghasilkan Face ID unik...")
        while True:
            face_id = random.randint(1000, 99999) # 5 digit random ID
            if not self.db_service.is_face_id_taken(face_id):
                break
        
        # 3. Logging & Konfirmasi
        print(f"[DEBUG] Registrasi Baru:")
        print(f"  - Tipe: {user_type}, Nama: {nama}, Info: {extra_data}")
        print(f"  - Face ID Dihasilkan: {face_id}")
        self.status_label.configure(text=f"Status: Face ID {face_id} dihasilkan untuk {nama}.")

        # 4. Simpan ke Database
        new_user_id = self.db_service.add_user(user_type, nama, extra_data, face_id)

        if new_user_id is None:
            messagebox.showerror("Gagal Database", "Gagal menyimpan data. Coba lagi.")
            self.status_label.configure(text="Status: Gagal menyimpan ke database.")
            return
        
        print(f"[DEBUG] Berhasil disimpan ke DB dengan ID: {new_user_id}")
        messagebox.showinfo("Data Tersimpan", f"Data untuk {nama} berhasil disimpan. Proses rekam wajah akan dimulai.")

        # 5. Mulai Rekam Wajah
        self.status_label.configure(text=f"Status: Memulai kamera untuk merekam wajah {nama}...")
        error = self.face_service.rekam_wajah(user_type, face_id, nama)
        if error:
            messagebox.showerror("Error Kamera", error)
            self.status_label.configure(text=f"Status: Gagal merekam wajah.")
        else:
            messagebox.showinfo("Sukses", f"Rekam wajah untuk {nama} selesai. Jangan lupa Latih Model.")
            self.status_label.configure(text=f"Status: Siap")
            # Kosongkan form setelah berhasil
            self.entry_nama.delete(0, 'end')
            self.entry_extra.delete(0, 'end')

    def handle_latih(self):
        # Latih kedua model (siswa dan guru) secara berurutan
        self.latih_button.configure(state="disabled", text="Sedang Melatih...")
        self.status_label.configure(text="Status: Memulai training model, mohon tunggu...")
        
        def training_task():
            self.update_status_from_thread("Melatih model Siswa...")
            self.face_service.latih_wajah('siswa', self.update_status_from_thread)
            
            self.update_status_from_thread("Melatih model Guru...")
            self.face_service.latih_wajah('guru', self.update_status_from_thread)
            
            self.update_status_from_thread("Semua model selesai dilatih.")

        threading.Thread(target=training_task, daemon=True).start()

    def update_status_from_thread(self, message):
        def update_gui():
            self.status_label.configure(text=f"Status: {message}")
            if "selesai dilatih" in message or "Tidak ada data" in message:
                self.latih_button.configure(state="normal", text="2. Latih Model (Global)")
                messagebox.showinfo("Proses Selesai", message)
        
        self.after(0, update_gui)

class AbsensiPage(ctk.CTkFrame):
    def __init__(self, parent, face_service):
        super().__init__(parent)
        self.face_service = face_service

        ctk.CTkLabel(self, text="Absensi Real-time", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=15)

        ctk.CTkButton(self, text="Mulai Absensi Siswa", command=lambda: self.run_absensi('siswa'), height=50).pack(pady=20, padx=50, fill="x")
        ctk.CTkButton(self, text="Mulai Absensi Guru", command=lambda: self.run_absensi('guru'), height=50).pack(pady=20, padx=50, fill="x")

    def run_absensi(self, user_type):
        error = self.face_service.absensi_wajah(user_type)
        if error:
            messagebox.showerror("Error Absensi", error)

if __name__ == "__main__":
    app = App()
    app.mainloop()