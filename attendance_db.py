import sqlite3

class AttendanceDB:
    def __init__(self, db_path='facesentry.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Tabel users
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                absen INTEGER,
                nama TEXT,
                kelas TEXT,
                UNIQUE(absen, kelas)
            )
        ''')
        # Tabel attendance dengan kolom kelas
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                nama TEXT,
                kelas TEXT,
                waktu TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        self.c.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nip TEXT UNIQUE,
    nama TEXT,
    mapel TEXT
    )
        ''')

        self.c.execute('''
            CREATE TABLE IF NOT EXISTS teacher_attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER,
    waktu TEXT,
    FOREIGN KEY(teacher_id) REFERENCES teachers(id)
    )
        ''')
        
        self.conn.commit()

    def insert_user(self, absen, nama, kelas):
        self.c.execute("INSERT OR IGNORE INTO users (absen, nama, kelas) VALUES (?, ?, ?)", (absen, nama, kelas))
        self.conn.commit()

    def get_user_id(self, absen, kelas):
        self.c.execute("SELECT id FROM users WHERE absen = ? AND kelas = ?", (absen, kelas))
        return self.c.fetchone()

    def insert_attendance(self, user_id, nama, kelas, waktu):
        self.c.execute("INSERT INTO attendance (user_id, nama, kelas, waktu) VALUES (?, ?, ?, ?)", (user_id, nama, kelas, waktu))
        self.conn.commit()

    def close(self):
        self.conn.close()
