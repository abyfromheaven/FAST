import cv2
import sqlite3
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
import customtkinter as ctk
import numpy as np
from config import db_path, latihDir, haarcascadePath

face_cascade = cv2.CascadeClassifier(haarcascadePath)

def absensiWajahSiswa():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(f"{latihDir}/training.xml")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS absensi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            kelas TEXT,
            waktu TEXT
        )
    """)

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

                    progressbar.set(face_detected_counter / target_counter)
                    progress_persen = int((face_detected_counter / target_counter) * 100)
                    progress_label.configure(text=f"Progres: {progress_persen}%")

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

                    if face_detected_counter >= target_counter:
                        waktu = datetime.now().strftime("%Y-%m-%d")
                        cur.execute("SELECT * FROM absensi WHERE nama = ? AND kelas = ? AND DATE(waktu) = ?", (nama, kelas, waktu))
                        if cur.fetchone() is None:
                            waktu_full = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            cur.execute("INSERT INTO absensi (nama, kelas, waktu) VALUES (?, ?, ?)", (nama, kelas, waktu_full))
                            conn.commit()
                            messagebox.showinfo("Absensi Berhasil", f"{nama} kelas ({kelas}) berhasil absen.")
                        else:
                            messagebox.showinfo("Info", f"{nama} kelas ({kelas}) sudah absen hari ini.")
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

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        imgtk = ImageTk.PhotoImage(image=img_pil)
        label_video.imgtk = imgtk
        label_video.configure(image=imgtk)

        window.after(30, update_frame)

    update_frame()