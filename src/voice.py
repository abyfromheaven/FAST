# suara.py
from gtts import gTTS
from playsound import playsound
import os

def ucap_dari_file(nama_file_teks, nama_audio="temp.mp3"):
    try:
        with open(nama_file_teks, "r", encoding="utf-8") as file:
            teks = file.read()

        tts = gTTS(text=teks, lang='id')
        tts.save(nama_audio)
        playsound(nama_audio)
        os.remove(nama_audio)
    except Exception as e:
        print(f"[SUARA ERROR] {e}")
