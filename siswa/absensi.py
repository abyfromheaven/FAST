import cv2
import sqlite3
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
import customtkinter as ctk
import numpy as np
from config import db_path, latihDir, haarcascadePath
from notifier import kirim_notifikasi_absensi_siswa
from voice import ucap_dari_file  # Import fungsi suara

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
    running = True

    def selesai_absen(nama, kelas, waktu_full):
        """Dipanggil saat absensi berhasil"""
        kirim_notifikasi_absensi_siswa(nama, kelas, waktu_full)

        with open("pesan_siswa.txt", "w", encoding="utf-8") as f:
            f.write(f"Absensi diterima. {nama} dari kelas {kelas}, semoga harimu penuh prestasi!")

        def lanjut_setelah_messagebox():
            ucap_dari_file("pesan_siswa.txt")
            window.destroy()

        messagebox.showinfo("Absensi Diterima", f"Siswa {nama} dari kelas ({kelas}) telah melakukan absensi.")
        window.after(100, lanjut_setelah_messagebox)

    def info_sudah_absen(nama, kelas):
        """Jika sudah absen hari ini"""
        def lanjut():
            window.destroy()
        messagebox.showinfo("Info", f"{nama} kelas ({kelas}) sudah absen hari ini.")
        window.after(100, lanjut)

    def update_frame():
        nonlocal face_detected_counter, running
        if not running:
            return

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

                    # Update Progress
                    progress = face_detected_counter / target_counter
                    progressbar.set(progress)
                    progress_label.configure(text=f"Progres: {int(progress * 100)}%")

                    # Tampilkan Nama & Kelas
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

                    # Jika progress penuh, lakukan absensi
                    if face_detected_counter >= target_counter:
                        running = False
                        cam.release()

                        tanggal = datetime.now().strftime("%Y-%m-%d")
                        cur.execute("SELECT * FROM absensi WHERE nama = ? AND kelas = ? AND DATE(waktu) = ?", (nama, kelas, tanggal))
                        if cur.fetchone() is None:
                            waktu_full = datetime.now().strftime("%Y %-d %B %H:%M")
                            cur.execute("INSERT INTO absensi (nama, kelas, waktu) VALUES (?, ?, ?)", (nama, kelas, waktu_full))
                            conn.commit()
                            selesai_absen(nama, kelas, waktu_full)
                        else:
                            info_sudah_absen(nama, kelas)
                        return
            else:
                face_detected_counter = 0
        else:
            face_detected_counter = 0

        # Update UI
        progressbar.set(face_detected_counter / target_counter)
        progress_label.configure(text=f"Progres: {int((face_detected_counter / target_counter) * 100)}%")

        # Tampilkan video
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 6)

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        imgtk = ImageTk.PhotoImage(image=img_pil)
        label_video.imgtk = imgtk
        label_video.configure(image=imgtk)

        window.after(30, update_frame)

    update_frame()
