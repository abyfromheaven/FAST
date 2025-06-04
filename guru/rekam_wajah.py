# rekam_wajah.py (guru)
import cv2
import sqlite3
from tkinter import messagebox
from config import db_path, wajahGuruDir, haarcascadePath

face_cascade = cv2.CascadeClassifier(haarcascadePath)

def rekamDataWajahGuru(nama, mapel):
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
            cv2.imwrite(f"{wajahGuruDir}/{nama}.{user_id}.{count}.jpg", wajah)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow('Rekam Wajah Guru', frame)
        if cv2.waitKey(1) == 27 or count >= 30:
            break

    cam.release()
    cv2.destroyAllWindows()
    messagebox.showinfo("Info", f"Wajah {nama} berhasil direkam dengan ID {user_id}.")
