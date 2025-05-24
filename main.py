import cv2
import os
import numpy as np
import sqlite3
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
import threading
from PIL import Image, ImageTk, ImageFont, ImageDraw
import time

# Inisialisasi GUI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
root.title("FaceSentri - Absensi Berbasis Wajah")
root.geometry("800x600")

# Path folder
wajahDir = 'datawajah'
latihDir = 'latihwajah'
wajahGuruDir = 'datawajah_guru'
latihGuruDir = 'latihwajah_guru'
haarcascadePath = 'haarcascade_frontalface_default.xml'
haarcascadeEyePath = 'haarcascade_eye.xml'
db_path = 'facesentry.db'

# Pastikan folder ada
for path in [wajahDir, latihDir, wajahGuruDir, latihGuruDir]:
    os.makedirs(path, exist_ok=True)

# Load Haar Cascades
face_cascade = cv2.CascadeClassifier(haarcascadePath)
eye_cascade = cv2.CascadeClassifier(haarcascadeEyePath)

# FUNGSI TAMBAHAN UNTUK DETEKSI MATA
def draw_eyes(frame, gray, x, y, w, h):
    roi_gray = gray[y:y+h, x:x+w]
    roi_color = frame[y:y+h, x:x+w]
    eyes = eye_cascade.detectMultiScale(roi_gray)
    for (ex, ey, ew, eh) in eyes:
        cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 255, 0), 2)

def rekamDataWajahSiswa():
    nama = entry_nama.get()
    kelas = entry_kelas.get()
    if not nama or not kelas:
        messagebox.showwarning("Peringatan", "Nama dan kelas harus diisi!")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS siswa (id INTEGER PRIMARY KEY AUTOINCREMENT, nama TEXT, kelas TEXT)")
    cur.execute("INSERT INTO siswa (nama, kelas) VALUES (?, ?)", (nama, kelas))
    user_id = cur.lastrowid
    conn.commit()
    conn.close()

    cam = cv2.VideoCapture(0)
    count = 0

    while True:
        ret, frame = cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            count += 1
            wajah = gray[y:y+h, x:x+w]
            cv2.imwrite(f"{wajahDir}/siswa.{user_id}.{count}.jpg", wajah)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Panggil fungsi untuk deteksi dan gambar mata
            draw_eyes(frame, gray, x, y, w, h)

        cv2.imshow('Rekam Wajah Siswa', frame)
        if cv2.waitKey(1) == 27 or count >= 30:
            break

    cam.release()
    cv2.destroyAllWindows()
    messagebox.showinfo("Info", f"Wajah siswa berhasil direkam dengan ID {user_id}.")

def trainingWajahSiswa():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, ids = [], []
    for file in os.listdir(wajahDir):
        if file.endswith(".jpg"):
            path = os.path.join(wajahDir, file)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            parts = file.split(".")
            if len(parts) > 2 and parts[1].isdigit():
                id = int(parts[1])
                faces.append(img)
                ids.append(id)
            else:
                print(f"File {file} diabaikan karena format nama tidak sesuai.")
    if faces and ids:
        recognizer.train(faces, np.array(ids))
        recognizer.write(os.path.join(latihDir, 'training.xml'))
        messagebox.showinfo("Info", "Model wajah siswa berhasil dilatih.")
    else:
        messagebox.showwarning("Peringatan", "Tidak ada data wajah yang valid untuk dilatih.")


def absensiWajahSiswa():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(os.path.join(latihDir, 'training.xml'))
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS absensi (id INTEGER PRIMARY KEY AUTOINCREMENT, nama TEXT, kelas TEXT, waktu TEXT)")

    window = ctk.CTkToplevel()
    window.title("Absensi Wajah Siswa")
    window.geometry("800x600")

    label_video = ctk.CTkLabel(window, text="")
    label_video.pack()

    progressbar = ctk.CTkProgressBar(window, width=500, height=20, progress_color="green")
    progressbar.pack(pady=(10, 5))
    progressbar.set(0)

    progress_label = ctk.CTkLabel(window, text="Progres: 0%")
    progress_label.pack()

    cam = cv2.VideoCapture(0)
    face_detected_counter = 0
    target_counter = 30

    def update_frame():
        nonlocal face_detected_counter
        ret, frame = cam.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            id_predicted, conf = recognizer.predict(gray[y:y+h, x:x+w])
            if conf < 100:
                cur.execute("SELECT nama, kelas FROM siswa WHERE id = ?", (id_predicted,))
                result = cur.fetchone()
                if result:
                    nama, kelas = result
                    face_detected_counter += 1

                    # Update progress bar dan label
                    progressbar.set(face_detected_counter / target_counter)
                    progress_persen = int((face_detected_counter / target_counter) * 100)
                    progress_label.configure(text=f"Progres: {progress_persen}%")

                    # Tampilkan nama dan kelas
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.7
                    thickness = 2
                    spacing = 10
                    (size1, _) = cv2.getTextSize(nama, font, font_scale, thickness)
                    (size2, _) = cv2.getTextSize(kelas, font, font_scale, thickness)
                    width = max(size1[0], size2[0])
                    x_rect = x
                    y_rect = y + h + 20
                    cv2.rectangle(frame, (x_rect - 5, y_rect - size1[1] - 10),
                                  (x_rect + width + 5, y_rect + size2[1] + spacing), (0, 255, 0), -1)
                    cv2.putText(frame, nama, (x_rect, y_rect), font, font_scale, (255, 255, 255), thickness)
                    cv2.putText(frame, kelas, (x_rect, y_rect + size2[1] + spacing),
                                font, font_scale, (255, 255, 255), thickness)

                    # Tambahkan deteksi mata di wajah yang dikenali
                    draw_eyes(frame, gray, x, y, w, h)

                    if face_detected_counter >= target_counter:
                        waktu = datetime.now().strftime("%Y-%m-%d")
                        cur.execute("SELECT * FROM absensi WHERE nama = ? AND kelas = ? AND DATE(waktu) = ?", (nama, kelas, waktu))
                        if cur.fetchone() is None:
                            waktu_full = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            cur.execute("INSERT INTO absensi (nama, kelas, waktu) VALUES (?, ?, ?)", (nama, kelas, waktu_full))
                            conn.commit()
                            messagebox.showinfo("Absensi Berhasil", f"{nama} ({kelas}) berhasil absen.")
                        else:
                            messagebox.showinfo("Info", f"{nama} ({kelas}) sudah absen hari ini.")
                        cam.release()
                        window.destroy()
                        return
            else:
                face_detected_counter = 0
        else:
            face_detected_counter = 0

        # Reset progress bar dan label jika wajah tidak dikenali atau tidak ada
        progressbar.set(face_detected_counter / target_counter)
        progress_persen = int((face_detected_counter / target_counter) * 100)
        progress_label.configure(text=f"Progres: {progress_persen}%")

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 6)
            # Tambahkan deteksi mata pada semua wajah yang terdeteksi
            draw_eyes(frame, gray, x, y, w, h)

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        imgtk = ImageTk.PhotoImage(image=img_pil)
        label_video.imgtk = imgtk
        label_video.configure(image=imgtk)

        window.after(30, update_frame)

    update_frame()

def rekamDataWajahGuru():
    nama = entry_guru_nama.get()
    mapel = entry_guru_mapel.get()
    if not nama or not mapel:
        messagebox.showwarning("Peringatan", "Nama dan mapel harus diisi!")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS guru (id INTEGER PRIMARY KEY AUTOINCREMENT, nama TEXT, mapel TEXT)")
    cur.execute("INSERT INTO guru (nama, mapel) VALUES (?, ?)", (nama, mapel))
    user_id = cur.lastrowid
    conn.commit()
    conn.close()

    cam = cv2.VideoCapture(0)
    count = 0

    while True:
        ret, frame = cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            count += 1
            wajah = gray[y:y+h, x:x+w]
            cv2.imwrite(f"{wajahGuruDir}/guru.{user_id}.{count}.jpg", wajah)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Tambahkan deteksi mata
            draw_eyes(frame, gray, x, y, w, h)

        cv2.imshow('Rekam Wajah Guru', frame)
        if cv2.waitKey(1) == 27 or count >= 30:
            break

    cam.release()
    cv2.destroyAllWindows()
    messagebox.showinfo("Info", f"Wajah guru berhasil direkam dengan ID {user_id}.")

def trainingWajahGuru():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, ids = [], []
    for file in os.listdir(wajahGuruDir):
        if file.endswith(".jpg"):
            path = os.path.join(wajahGuruDir, file)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            id = int(file.split(".")[1])
            faces.append(img)
            ids.append(id)
    recognizer.train(faces, np.array(ids))
    recognizer.write(os.path.join(latihGuruDir, 'training_guru.xml'))
    messagebox.showinfo("Info", "Model wajah guru berhasil dilatih.")


def absensiWajahGuru():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(os.path.join(latihGuruDir, 'training_guru.xml'))
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS absensi_guru (id INTEGER PRIMARY KEY AUTOINCREMENT, nama TEXT, mapel TEXT, waktu TEXT)")

    window = ctk.CTkToplevel()
    window.title("Absensi Wajah Guru")
    window.geometry("800x600")

    label_video = ctk.CTkLabel(window, text="")
    label_video.pack()

    progressbar = ctk.CTkProgressBar(window, width=500, height=20, progress_color="green")
    progressbar.pack(pady=(10, 5))
    progressbar.set(0)

    progress_label = ctk.CTkLabel(window, text="Progres: 0%")
    progress_label.pack()

    cam = cv2.VideoCapture(0)
    face_detected_counter = 0
    target_counter = 30

    def update_frame():
        nonlocal face_detected_counter
        ret, frame = cam.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            id_predicted, conf = recognizer.predict(gray[y:y+h, x:x+w])
            if conf < 100:
                cur.execute("SELECT nama, mapel FROM guru WHERE id = ?", (id_predicted,))
                result = cur.fetchone()
                if result:
                    nama, mapel = result
                    face_detected_counter += 1

                    progressbar.set(face_detected_counter / target_counter)
                    progress_persen = int((face_detected_counter / target_counter) * 100)
                    progress_label.configure(text=f"Progres: {progress_persen}%")

                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.7
                    thickness = 2
                    spacing = 10
                    (size1, _) = cv2.getTextSize(nama, font, font_scale, thickness)
                    (size2, _) = cv2.getTextSize(mapel, font, font_scale, thickness)
                    width = max(size1[0], size2[0])
                    x_rect = x
                    y_rect = y + h + 20
                    cv2.rectangle(frame, (x_rect - 5, y_rect - size1[1] - 10),
                                  (x_rect + width + 5, y_rect + size2[1] + spacing), (0, 255, 0), -1)
                    cv2.putText(frame, nama, (x_rect, y_rect), font, font_scale, (255, 255, 255), thickness)
                    cv2.putText(frame, mapel, (x_rect, y_rect + size2[1] + spacing),
                                font, font_scale, (255, 255, 255), thickness)

                    # Tambahkan deteksi mata
                    draw_eyes(frame, gray, x, y, w, h)

                    if face_detected_counter >= target_counter:
                        waktu = datetime.now().strftime("%Y-%m-%d")
                        cur.execute("SELECT * FROM absensi_guru WHERE nama = ? AND mapel = ? AND DATE(waktu) = ?", (nama, mapel, waktu))
                        if cur.fetchone() is None:
                            waktu_full = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            cur.execute("INSERT INTO absensi_guru (nama, mapel, waktu) VALUES (?, ?, ?)", (nama, mapel, waktu_full))
                            conn.commit()
                            messagebox.showinfo("Absensi Berhasil", f"{nama} ({mapel}) berhasil absen.")
                        else:
                            messagebox.showinfo("Info", f"{nama} ({mapel}) sudah absen hari ini.")
                        cam.release()
                        window.destroy()
                        return
            else:
                face_detected_counter = 0
        else:
            face_detected_counter = 0

        progressbar.set(face_detected_counter / target_counter)
        progress_persen = int((face_detected_counter / target_counter) * 100)
        progress_label.configure(text=f"Progres: {progress_persen}%")

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 6)
            # Tambahkan deteksi mata
            draw_eyes(frame, gray, x, y, w, h)

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        imgtk = ImageTk.PhotoImage(image=img_pil)
        label_video.imgtk = imgtk
        label_video.configure(image=imgtk)

        window.after(30, update_frame)

    update_frame()

# Tampilan GUI
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

ctk.CTkButton(frame_inputs_siswa, text="Rekam Wajah", command=rekamDataWajahSiswa).grid(row=2, column=0, padx=10, pady=10)
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

ctk.CTkButton(frame_inputs_guru, text="Rekam Wajah", command=rekamDataWajahGuru).grid(row=2, column=0, padx=10, pady=10)
ctk.CTkButton(frame_inputs_guru, text="Latih Model Wajah", command=trainingWajahGuru).grid(row=2, column=1, padx=10, pady=10)
ctk.CTkButton(frame_inputs_guru, text="Absensi Wajah", command=absensiWajahGuru).grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
