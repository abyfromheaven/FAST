
import os

# Direktori dasar proyek
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ID Kamera yang digunakan
CAMERA_ID = 0

# =====================================================================
# PATHS - Semua path penting ada di sini
# =====================================================================

# Path untuk file classifier Haar Cascade
HAARCASCADE_PATH = os.path.join(BASE_DIR, 'assets', 'resources', 'haarcascade_frontalface_default.xml')

# Path untuk direktori data
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATASETS_DIR = os.path.join(DATA_DIR, 'datasets')
MODELS_DIR = os.path.join(DATA_DIR, 'models')

# Path untuk file database SQLite
DATABASE_PATH = os.path.join(DATA_DIR, 'facesentry.db')

# Path spesifik untuk dataset siswa dan guru
SISWA_DATASET_PATH = os.path.join(DATASETS_DIR, 'siswa')
GURU_DATASET_PATH = os.path.join(DATASETS_DIR, 'guru')

# Path spesifik untuk model training siswa dan guru
SISWA_MODEL_PATH = os.path.join(MODELS_DIR, 'siswa_model.xml')
GURU_MODEL_PATH = os.path.join(MODELS_DIR, 'guru_model.xml')


# =====================================================================
# PENGATURAN MODEL - Pengaturan untuk recognizer dan training
# =====================================================================

# Confidence threshold untuk recognizer (LBPH). Nilai di bawah ini dianggap cocok.
RECOGNIZER_CONFIDENCE_THRESHOLD = 65

# Ukuran gambar yang konsisten untuk training
TRAINING_IMAGE_SIZE = (100, 100)

# Jumlah sampel wajah yang akan diambil per orang
MAX_SAMPLES = 30

# Frame-skip untuk deteksi wajah (deteksi setiap N frame)
FRAME_SKIP = 4 # Deteksi dilakukan setiap 4 frame
