
import cv2
from datetime import datetime
import os
import numpy as np
from PIL import Image
import config

class FaceService:
    def __init__(self, db_service):
        '''Menginisialisasi layanan pengenalan wajah.

        Args:
            db_service (DatabaseService): Instance dari layanan database.
        '''
        self.db_service = db_service
        self.face_cascade = self._load_cascade()

    def _load_cascade(self):
        '''Memuat Haar Cascade classifier dan menangani error jika file tidak ada.'''
        if not os.path.exists(config.HAARCASCADE_PATH):
            print(f"[FATAL ERROR] File Haar Cascade tidak ditemukan di: {config.HAARCASCADE_PATH}")
            # Di aplikasi nyata, ini akan menampilkan popup error sebelum keluar
            raise FileNotFoundError(f"Haar Cascade not found at {config.HAARCASCADE_PATH}")
        return cv2.CascadeClassifier(config.HAARCASCADE_PATH)

    def _get_paths(self, user_type: str):
        '''Mendapatkan path dataset dan model berdasarkan tipe pengguna.'''
        if user_type == 'siswa':
            return config.SISWA_DATASET_PATH, config.SISWA_MODEL_PATH
        elif user_type == 'guru':
            return config.GURU_DATASET_PATH, config.GURU_MODEL_PATH
        else:
            raise ValueError("Tipe pengguna tidak valid. Harus 'siswa' atau 'guru'.")

    def rekam_wajah(self, user_type: str, user_id: int, user_name: str):
        '''Fungsi terpadu untuk merekam data wajah baru dengan penanganan error.'''
        dataset_path, _ = self._get_paths(user_type)
        user_folder_path = os.path.join(dataset_path, f"{user_id}.{user_name}")
        os.makedirs(user_folder_path, exist_ok=True)

        cam = cv2.VideoCapture(config.CAMERA_ID)
        if not cam.isOpened():
            print("[CAMERA ERROR] Tidak dapat membuka kamera. Pastikan kamera terhubung.")
            return "Kamera tidak ditemukan"

        print("\n[INFO] Inisialisasi pengambilan wajah. Lihat ke kamera dan tunggu...")
        sample_count = 0

        while sample_count < config.MAX_SAMPLES:
            ret, frame = cam.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                sample_count += 1
                
                # Resize gambar sebelum disimpan untuk konsistensi
                face_resized = cv2.resize(gray[y:y+h, x:x+w], config.TRAINING_IMAGE_SIZE)
                
                file_path = os.path.join(user_folder_path, f"user.{user_id}.{sample_count}.jpg")
                cv2.imwrite(file_path, face_resized)

                cv2.imshow('Rekam Wajah', frame)

            if cv2.waitKey(100) & 0xFF == 27:
                break

        cam.release()
        cv2.destroyAllWindows()
        print(f"\n[INFO] {sample_count} sampel wajah berhasil diambil.")
        return None # Tidak ada error

    def latih_wajah(self, user_type: str, update_gui_callback=None):
        '''Fungsi untuk melatih model dari dataset, dirancang untuk berjalan di thread.'''
        if update_gui_callback:
            update_gui_callback("Mulai proses training...")

        dataset_path, model_path = self._get_paths(user_type)
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        def get_images_and_labels(path):
            face_samples = []
            ids = []
            if not os.path.exists(path):
                return [], []
            
            # Mengambil data user dari database untuk memastikan face_id valid
            users_from_db = self.db_service.get_all_users_for_training(user_type)
            valid_face_ids = users_from_db.keys()

            for root, dirs, files in os.walk(path):
                for dir_name in dirs:
                    try:
                        # Di sini, kita asumsikan nama folder adalah face_id.Nama
                        face_id = int(dir_name.split('.')[0])
                        if face_id not in valid_face_ids:
                            print(f"[TRAINING WARNING] Folder {dir_name} tidak sesuai dengan face_id di database, akan dilewati.")
                            continue

                        user_folder_path = os.path.join(root, dir_name)
                        for file_name in os.listdir(user_folder_path):
                            if file_name.endswith(('.jpg', '.png', '.jpeg')):
                                image_path = os.path.join(user_folder_path, file_name)
                                pil_image = Image.open(image_path).convert('L')
                                img_numpy = np.array(pil_image, 'uint8')
                                face_samples.append(img_numpy)
                                ids.append(face_id)
                    except (ValueError, IndexError):
                        print(f"[TRAINING WARNING] Format folder {dir_name} salah, akan dilewati.")
                        continue
            return face_samples, ids

        faces, ids = get_images_and_labels(dataset_path)
        
        if not faces:
            msg = "Tidak ada data wajah valid untuk dilatih."
            print(f"[TRAINING ERROR] {msg}")
            if update_gui_callback: update_gui_callback(msg)
            return

        recognizer.train(faces, np.array(ids))
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        recognizer.write(model_path)

        msg = f"{len(np.unique(ids))} wajah berhasil dilatih. Model disimpan."
        print(f"[TRAINING INFO] {msg}")
        if update_gui_callback: update_gui_callback(msg)

    def absensi_wajah(self, user_type: str):
        '''Fungsi terpadu untuk absensi dengan optimasi dan penanganan error.'''
        _, model_path = self._get_paths(user_type)

        if not os.path.exists(model_path):
            return f"Model untuk {user_type} tidak ditemukan. Latih model terlebih dahulu."

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(model_path)
        
        # Mengambil data user dari database, bukan dari folder
        users = self.db_service.get_all_users_for_training(user_type)
        if not users:
            print(f"[WARNING] Tidak ada data {user_type} yang terdaftar di database.")

        cam = cv2.VideoCapture(config.CAMERA_ID)
        if not cam.isOpened():
            return "Kamera tidak ditemukan."

        font = cv2.FONT_HERSHEY_SIMPLEX
        frame_count = 0
        
        # Set untuk melacak user yang sudah dideteksi dalam beberapa detik terakhir
        recently_detected = set()
        detection_timers = {}

        window_title = f"Absensi {user_type.capitalize()}"

        while True:
            ret, frame = cam.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Optimasi: Deteksi wajah hanya setiap N frame
            faces = self.face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(100, 100))

            current_time = datetime.now().timestamp()

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                face_id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

                display_text = "Tidak Dikenali"
                if confidence < config.RECOGNIZER_CONFIDENCE_THRESHOLD:
                    user_name = users.get(face_id, "Tidak Ditemukan")
                    display_text = user_name
                    confidence_text = f"  {round(100 - confidence)}%"
                    
                    # Mencegah pencatatan berulang kali dalam waktu singkat
                    if face_id not in recently_detected:
                        user_info = self.db_service.get_user_by_face_id(face_id)
                        if user_info:
                            # Panggil service database dengan menyertakan nama
                            self.db_service.record_attendance(user_info['id'], user_info['name'], user_info['type'])
                            
                            # Tambahkan user ke set 'recently_detected'
                            recently_detected.add(face_id)
                            detection_timers[face_id] = current_time
                else:
                    confidence_text = f"  {round(100 - confidence)}%"

                cv2.putText(frame, display_text, (x + 5, y - 5), font, 1, (255, 255, 255), 2)
                cv2.putText(frame, confidence_text, (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

            # Membersihkan user dari 'recently_detected' setelah beberapa detik
            cooldown_period = 5 # detik
            users_to_remove = [uid for uid, t in detection_timers.items() if current_time - t > cooldown_period]
            for uid in users_to_remove:
                recently_detected.remove(uid)
                del detection_timers[uid]

            cv2.imshow(window_title, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27 or cv2.getWindowProperty(window_title, cv2.WND_PROP_VISIBLE) < 1:
                break

        cam.release()
        cv2.destroyAllWindows()
        return None # Tidak ada error
