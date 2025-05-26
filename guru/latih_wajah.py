import os
import cv2
import numpy as np
from tkinter import messagebox
from config import wajahGuruDir, latihGuruDir

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
    if faces and ids:
        recognizer.train(faces, np.array(ids))
        recognizer.write(os.path.join(latihGuruDir, 'training_guru.xml'))
        messagebox.showinfo("Info", "Model wajah guru berhasil dilatih.")
    else:
        messagebox.showwarning("Peringatan", "Tidak ada data wajah yang valid untuk dilatih.")

