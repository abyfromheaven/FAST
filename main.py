import cv2
import os
import numpy as np
import customtkinter as ctk
from PIL import Image
from datetime import datetime
import attendance_db  # Import modul database yang terpisah

# Inisialisasi database
db = attendance_db.AttendanceDB('facesentry.db')

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Fungsi untuk merekam wajah siswa
def rekamDataWajahSiswa():
    wajahDir = 'datawajah'
    os.makedirs(wajahDir, exist_ok=True)
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)
    faceDetector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    nama = entry1.get()
    absen = entry2.get()
    kelas = entry3.get()

    # Simpan data user ke DB (jika belum ada)
    db.insert_user(absen, nama, kelas)

    ambilData = 1
    while True:
        retV, frame = cam.read()
        abuabu = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceDetector.detectMultiScale(abuabu, 1.3, 5)
        for (x, y, w, h) in faces:
            frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
            namaFile = f"{absen}_{nama}_{kelas}_{ambilData}.jpg"
            cv2.imwrite(os.path.join(wajahDir, namaFile), frame)
            ambilData += 1
        cv2.imshow('webcamku', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        elif ambilData > 30:
            break
    cam.release()
    cv2.destroyAllWindows()

# Fungsi untuk melatih wajah siswa
def trainingWajahSiswa():
    wajahDir = 'datawajah'
    latihDir = 'latihwajah'
    os.makedirs(latihDir, exist_ok=True)

    def getImageLabel(path):
        imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith('.jpg')]
        faceSamples = []
        faceIDs = []
        faceDetector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        for imagePath in imagePaths:
            PILimg = Image.open(imagePath).convert('L')
            imgNum = np.array(PILimg, 'uint8')
            faceID = int(os.path.split(imagePath)[-1].split('_')[0])
            faces = faceDetector.detectMultiScale(imgNum)
            for (x, y, w, h) in faces:
                faceSamples.append(imgNum[y:y + h, x:x + w])
                faceIDs.append(faceID)
        return faceSamples, faceIDs

    faceRecognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, IDs = getImageLabel(wajahDir)
    if faces and IDs:
        faceRecognizer.train(faces, np.array(IDs))
        faceRecognizer.write(os.path.join(latihDir, 'training.xml'))

# Fungsi untuk absensi siswa
def absensiWajahSiswa():
    latihDir = 'latihwajah'
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)
    faceDetector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    faceRecognizer = cv2.face.LBPHFaceRecognizer_create()
    faceRecognizer.read(os.path.join(latihDir, 'training.xml'))

    absen = entry2.get()
    kelas = entry3.get()
    nama = entry1.get()

    while True:
        retV, frame = cam.read()
        frame = cv2.flip(frame, 1)
        abuabu = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceDetector.detectMultiScale(abuabu, 1.2, 5)
        for (x, y, w, h) in faces:
            id_predicted, confidence = faceRecognizer.predict(abuabu[y:y + h, x:x + w])
            if confidence < 100:
                markAttendanceSiswa(id_predicted, nama, kelas)
        cv2.imshow('ABSENSI WAJAH', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

def markAttendanceSiswa(id_predicted, nama, kelas):
    user = db.get_user_id(id_predicted, kelas)
    if user:
        user_id = user[0]
        now = datetime.now()
        dtString = now.strftime('%H:%M:%S')
        db.insert_attendance(user_id, nama, kelas, dtString)

# Fungsi untuk merekam wajah guru
def rekamDataWajahGuru():
    wajahDir = 'datawajah_guru'
    os.makedirs(wajahDir, exist_ok=True)
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)
    faceDetector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    nama = entry_guru_nama.get()
    nip = entry_guru_nip.get()
    mapel = entry_guru_mapel.get()

    # Simpan data guru ke DB (jika belum ada)
    db.c.execute("INSERT OR IGNORE INTO teachers (nip, nama, mapel) VALUES (?, ?, ?)", (nip, nama, mapel))
    db.conn.commit()

    ambilData = 1
    while True:
        retV, frame = cam.read()
        abuabu = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceDetector.detectMultiScale(abuabu, 1.3, 5)
        for (x, y, w, h) in faces:
            frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
            namaFile = f"{nip}_{nama}_{ambilData}.jpg"
            cv2.imwrite(os.path.join(wajahDir, namaFile), frame)
            ambilData += 1
        cv2.imshow('webcamku', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        elif ambilData > 30:
            break
    cam.release()
    cv2.destroyAllWindows()

# Fungsi untuk melatih wajah guru
def trainingWajahGuru():
    wajahDir = 'datawajah_guru'
    latihDir = 'latihwajah_guru'
    os.makedirs(latihDir, exist_ok=True)

    def getImageLabel(path):
        imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith('.jpg')]
        faceSamples = []
        faceIDs = []
        faceDetector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        for imagePath in imagePaths:
            PILimg = Image.open(imagePath).convert('L')
            imgNum = np.array(PILimg, 'uint8')
            faceID = int(os.path.split(imagePath)[-1].split('_')[0])
            faces = faceDetector.detectMultiScale(imgNum)
            for (x, y, w, h) in faces:
                faceSamples.append(imgNum[y:y + h, x:x + w])
                faceIDs.append(faceID)
        return faceSamples, faceIDs

    faceRecognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, IDs = getImageLabel(wajahDir)
    if faces and IDs:
        faceRecognizer.train(faces, np.array(IDs))
        faceRecognizer.write(os.path.join(latihDir, 'training_guru.xml'))

# Fungsi untuk absensi guru
def absensiWajahGuru():
    latihDir = 'latihwajah_guru'
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)
    faceDetector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    faceRecognizer = cv2.face.LBPHFaceRecognizer_create()
    faceRecognizer.read(os.path.join(latihDir, 'training_guru.xml'))

    nip = entry_guru_nip.get()
    nama = entry_guru_nama.get()

    while True:
        retV, frame = cam.read()
        frame = cv2.flip(frame, 1)
        abuabu = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceDetector.detectMultiScale(abuabu, 1.2, 5)
        for (x, y, w, h) in faces:
            id_predicted, confidence = faceRecognizer.predict(abuabu[y:y + h, x:x + w])
            if confidence < 100:
                markAttendanceGuru(id_predicted, nama)
        cv2.imshow('ABSENSI WAJAH GURU', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

def markAttendanceGuru(id_predicted, nama):
    user = db.c.execute("SELECT id FROM teachers WHERE nip = ?", (id_predicted,)).fetchone()
    if user:
        teacher_id = user[0]
        now = datetime.now()
        dtString = now.strftime('%H:%M:%S')
        db.c.execute("INSERT INTO teacher_attendance (teacher_id, waktu) VALUES (?, ?)", (teacher_id, dtString))
        db.conn.commit()

# GUI dengan customtkinter
root = ctk.CTk()
root.geometry("800x600")
root.title("FaceSentry - Smart Attendance")

tabview = ctk.CTkTabview(root)
tabview.pack(pady=20, padx=20, fill="both", expand=True)

# Tab Siswa
tab_siswa = tabview.add("Siswa")
frame_inputs_siswa = ctk.CTkFrame(tab_siswa)
frame_inputs_siswa.pack(pady=20, padx=20, fill="x")

ctk.CTkLabel(frame_inputs_siswa, text="Nama Siswa").grid(row=0, column=0, padx=5, pady=10, sticky="w")
entry1 = ctk.CTkEntry(frame_inputs_siswa)
entry1.grid(row=0, column=1, padx=5, pady=10)

ctk.CTkLabel(frame_inputs_siswa, text="Nomor Absen").grid(row=1, column=0, padx=5, pady=10, sticky="w")
entry2 = ctk.CTkEntry(frame_inputs_siswa)
entry2.grid(row=1, column=1, padx=5, pady=10)

ctk.CTkLabel(frame_inputs_siswa, text="Kelas").grid(row=2, column=0, padx=5, pady=10, sticky="w")
entry3 = ctk.CTkEntry(frame_inputs_siswa)
entry3.grid(row=2, column=1, padx=5, pady=10)

ctk.CTkButton(frame_inputs_siswa, text="Rekam Wajah", command=rekamDataWajahSiswa).grid(row=3, column=0, padx=10, pady=10)
ctk.CTkButton(frame_inputs_siswa, text="Latih Model Wajah", command=trainingWajahSiswa).grid(row=3, column=1, padx=10, pady=10)
ctk.CTkButton(frame_inputs_siswa, text="Absen Kehadiran", command=absensiWajahSiswa).grid(row=3, column=2, padx=10, pady=10)

# Tab Guru
tab_guru = tabview.add("Guru")
frame_inputs_guru = ctk.CTkFrame(tab_guru)
frame_inputs_guru.pack(pady=20, padx=20, fill="x")

ctk.CTkLabel(frame_inputs_guru, text="Nama Guru").grid(row=0, column=0, padx=5, pady=10, sticky="w")
entry_guru_nama = ctk.CTkEntry(frame_inputs_guru)
entry_guru_nama.grid(row=0, column=1, padx=5, pady=10)

ctk.CTkLabel(frame_inputs_guru, text="NIP").grid(row=1, column=0, padx=5, pady=10, sticky="w")
entry_guru_nip = ctk.CTkEntry(frame_inputs_guru)
entry_guru_nip.grid(row=1, column=1, padx=5, pady=10)

ctk.CTkLabel(frame_inputs_guru, text="Mata Pelajaran").grid(row=2, column=0, padx=5, pady=10, sticky="w")
entry_guru_mapel = ctk.CTkEntry(frame_inputs_guru)
entry_guru_mapel.grid(row=2, column=1, padx=5, pady=10)

ctk.CTkButton(frame_inputs_guru, text="Rekam Wajah", command=rekamDataWajahGuru).grid(row=3, column=0, padx=10, pady=10)
ctk.CTkButton(frame_inputs_guru, text="Latih Model Wajah", command=trainingWajahGuru).grid(row=3, column=1, padx=10, pady=10)
ctk.CTkButton(frame_inputs_guru, text="Absen Kehadiran", command=absensiWajahGuru).grid(row=3, column=2, padx=10, pady=10)

# Tutup koneksi database saat aplikasi ditutup
import atexit
atexit.register(db.close)

root.mainloop()
