import customtkinter as ctk
from siswa.rekam_wajah import rekamDataWajahSiswa
from siswa.latih_wajah import trainingWajahSiswa
from siswa.absensi import absensiWajahSiswa
from guru.rekam_wajah import rekamDataWajahGuru
from guru.latih_wajah import trainingWajahGuru
from guru.absensi import absensiWajahGuru

def setup_gui(root):
    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=20, padx=20, fill="both", expand=True)
    tabview = ctk.CTkTabview(frame)
    tabview.pack(expand=True, fill="both")

    # Tab Siswa
    tab_siswa = tabview.add("Siswa")
    frame_inputs_siswa = ctk.CTkFrame(tab_siswa)
    frame_inputs_siswa.pack(pady=20, padx=20, fill="x")

    ctk.CTkLabel(frame_inputs_siswa, text="Nama Siswa").grid(row=0, column=0, padx=5, pady=10, sticky="w")
    entry_nama = ctk.CTkEntry(frame_inputs_siswa)
    entry_nama.grid(row=0, column=1, padx=5, pady=10)

    ctk.CTkLabel(frame_inputs_siswa, text="Kelas").grid(row=1, column=0, padx=5, pady=10, sticky="w")
    entry_kelas = ctk.CTkEntry(frame_inputs_siswa)
    entry_kelas.grid(row=1, column=1, padx=5, pady=10)

    ctk.CTkButton(frame_inputs_siswa, text="Rekam Wajah", command=lambda: rekamDataWajahSiswa(entry_nama, entry_kelas)).grid(row=2, column=0, padx=10, pady=10)
    ctk.CTkButton(frame_inputs_siswa, text="Latih Model Wajah", command=trainingWajahSiswa).grid(row=2, column=1, padx=10, pady=10)
    ctk.CTkButton(frame_inputs_siswa, text="Absensi Wajah", command=absensiWajahSiswa).grid(row=3, column=0, columnspan=2, pady=10)

    # Tab Guru
    tab_guru = tabview.add("Guru")
    frame_inputs_guru = ctk.CTkFrame(tab_guru)
    frame_inputs_guru.pack(pady=20, padx=20, fill="x")

    ctk.CTkLabel(frame_inputs_guru, text="Nama Guru").grid(row=0, column=0, padx=5, pady=10, sticky="w")
    entry_guru_nama = ctk.CTkEntry(frame_inputs_guru)
    entry_guru_nama.grid(row=0, column=1, padx=5, pady=10)

    ctk.CTkLabel(frame_inputs_guru, text="Mata Pelajaran").grid(row=1, column=0, padx=5, pady=10, sticky="w")
    entry_guru_mapel = ctk.CTkEntry(frame_inputs_guru)
    entry_guru_mapel.grid(row=1, column=1, padx=5, pady=10)

    ctk.CTkButton(frame_inputs_guru, text="Rekam Wajah", command=lambda: rekamDataWajahGuru(entry_guru_nama, entry_guru_mapel)).grid(row=2, column=0, padx=10, pady=10)
    ctk.CTkButton(frame_inputs_guru, text="Latih Model Wajah", command=trainingWajahGuru).grid(row=2, column=1, padx=10, pady=10)
    ctk.CTkButton(frame_inputs_guru, text="Absensi Wajah", command=absensiWajahGuru).grid(row=3, column=0, columnspan=2, pady=10)
