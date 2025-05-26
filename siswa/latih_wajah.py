import os
import cv2
import numpy as np
from tkinter import messagebox
from config import wajahDir, latihDir

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