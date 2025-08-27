import sqlite3
import os
from datetime import datetime

# --- Konfigurasi Logging Sederhana ---
def log_info(message):
    """Mencatat pesan informasi ke terminal."""
    print(f"[DB INFO] {message}")

def log_error(message):
    """Mencatat pesan error ke terminal."""
    print(f"[DB ERROR] {message}")

class DatabaseService:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def _get_connection(self):
        try:
            db_dir = os.path.dirname(self.db_path)
            os.makedirs(db_dir, exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as e:
            log_error(f"Gagal membuat koneksi database: {e}")
            return None

    def init_db(self):
        """
        Membuat/Memvalidasi 4 tabel utama.
        - Kolom 'catatan' di tabel kehadiran diganti dengan 'kelas' (untuk siswa) 
        - dan 'subject' (untuk guru).
        """
        query_students = """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            face_id INTEGER UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        query_teachers = """
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            face_id INTEGER UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        query_attendance_students = """
        CREATE TABLE IF NOT EXISTS attendance_students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            class TEXT NOT NULL, -- Menggantikan 'catatan'
            date TEXT NOT NULL,
            time_in TEXT,
            time_out TEXT,
            status TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
        );
        """
        query_attendance_teachers = """
        CREATE TABLE IF NOT EXISTS attendance_teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            subject TEXT NOT NULL, -- Menggantikan 'catatan'
            date TEXT NOT NULL,
            time_in TEXT,
            time_out TEXT,
            status TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id) ON DELETE CASCADE
        );
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                log_info("Inisialisasi/Validasi skema database...")
                cursor.execute(query_students)
                cursor.execute(query_teachers)
                cursor.execute(query_attendance_students)
                cursor.execute(query_attendance_teachers)
                conn.commit()
                log_info("Skema database terbaru telah siap.")
        except sqlite3.Error as e:
            log_error(f"Gagal menginisialisasi tabel: {e}")
            raise e

    def add_user(self, user_type, name, class_or_subject, face_id):
        # ... (Fungsi ini tidak perlu diubah)
        if user_type == 'siswa':
            query = "INSERT INTO students (name, class, face_id) VALUES (?, ?, ?)"
        else:
            query = "INSERT INTO teachers (name, subject, face_id) VALUES (?, ?, ?)"
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name, class_or_subject, face_id))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            log_error(f"Gagal menambahkan user {name}: {e}")
            return None

    def get_user_by_face_id(self, face_id):
        # ... (Fungsi ini tidak perlu diubah)
        queries = {
            'siswa': "SELECT id, name FROM students WHERE face_id = ?",
            'guru': "SELECT id, name FROM teachers WHERE face_id = ?"
        }
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                for user_type, query in queries.items():
                    cursor.execute(query, (face_id,))
                    result = cursor.fetchone()
                    if result:
                        return {'id': result[0], 'name': result[1], 'type': user_type}
                return None
        except sqlite3.Error as e:
            log_error(f"Gagal mencari user dengan Face ID {face_id}: {e}")
            return None

    def is_face_id_taken(self, face_id):
        # ... (Fungsi ini tidak perlu diubah)
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT EXISTS(SELECT 1 FROM students WHERE face_id = ?)", (face_id,))
                if cursor.fetchone()[0]: return True
                cursor.execute("SELECT EXISTS(SELECT 1 FROM teachers WHERE face_id = ?)", (face_id,))
                if cursor.fetchone()[0]: return True
                return False
        except sqlite3.Error as e:
            log_error(f"Gagal memeriksa face_id {face_id}: {e}")
            return True

    def get_all_users_for_training(self, user_type):
        """Mengambil semua face_id dan nama untuk proses training model."""
        if user_type == 'siswa':
            table_name = 'students'
        elif user_type == 'guru':
            table_name = 'teachers'
        else:
            log_error(f"Tipe user tidak valid untuk training: {user_type}")
            return {}
        
        query = f"SELECT face_id, name FROM {table_name}"
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                # Membuat dictionary dari {face_id: name}
                users = {row[0]: row[1] for row in cursor.fetchall()}
                log_info(f"Mengambil {len(users)} user dari tabel {table_name} untuk training.")
                return users
        except sqlite3.Error as e:
            log_error(f"Gagal mengambil data user '{user_type}' untuk training: {e}")
            return {}

    def record_attendance(self, user_id, user_name, user_type):
        """Mencatat absensi dan menyertakan data kelas/mapel secara otomatis."""
        today = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M:%S")

        if user_type == 'siswa':
            table_attendance = "attendance_students"
            fk_column = "student_id"
            source_table = "students"
            extra_column_name = "class"
        elif user_type == 'guru':
            table_attendance = "attendance_teachers"
            fk_column = "teacher_id"
            source_table = "teachers"
            extra_column_name = "subject"
        else:
            log_error(f"Tipe user tidak valid untuk absensi: {user_type}")
            return

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Ambil data kelas/mapel dari tabel sumber
                cursor.execute(f"SELECT {extra_column_name} FROM {source_table} WHERE id = ?", (user_id,))
                result = cursor.fetchone()
                extra_data = result[0] if result else "N/A"

                # Cek apakah sudah ada catatan absensi untuk hari ini
                cursor.execute(
                    f"SELECT id, time_out FROM {table_attendance} WHERE {fk_column} = ? AND date = ?",
                    (user_id, today)
                )
                record = cursor.fetchone()

                if record is None:
                    # Belum ada, catat sebagai absensi masuk (check-in)
                    status = "Hadir"
                    cursor.execute(
                        f"INSERT INTO {table_attendance} ({fk_column}, name, {extra_column_name}, date, time_in, status) VALUES (?, ?, ?, ?, ?, ?)",
                        (user_id, user_name, extra_data, today, now_time, status)
                    )
                    log_info(f"Absensi MASUK: {user_name} ({extra_data}) pada {now_time}")
                elif record[1] is None:
                    # Sudah ada check-in, catat sebagai absensi pulang (check-out)
                    record_id = record[0]
                    cursor.execute(
                        f"UPDATE {table_attendance} SET time_out = ? WHERE id = ?",
                        (now_time, record_id)
                    )
                    log_info(f"Absensi PULANG: {user_name} ({extra_data}) pada {now_time}")
                else:
                    # Sudah check-in dan check-out
                    log_info(f"{user_name} sudah lengkap absensinya hari ini.")
                
                conn.commit()
        except sqlite3.Error as e:
            log_error(f"Gagal mencatat absensi untuk {user_name}: {e}")