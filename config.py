import os

wajahDir = 'datawajah'
latihDir = 'latihwajah'
wajahGuruDir = 'datawajah_guru'
latihGuruDir = 'latihwajah_guru'

haarcascadePath = 'haarcascade_frontalface_default.xml'
haarcascadeEyePath = 'haarcascade_eye.xml'
db_path = 'facesentry.db'

for path in [wajahDir, latihDir, wajahGuruDir, latihGuruDir]:
    os.makedirs(path, exist_ok=True)
