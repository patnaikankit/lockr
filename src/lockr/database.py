import sqlite3
import os
import platform
import base64

APP_NAME="lockr"
DB_FILENAME="lockr.db"

class DatabaseManager:
    def __init__(self, app_name=APP_NAME, db_filename=DB_FILENAME):
        self.app_name = app_name
        self.db_filename = db_filename
        self.DB_PATH = self._get_app_data_directory()
        self._initialize_database()

        def _get_app_data_directory(self):
            # Fetch os and app details
            app_name = self.app_name
            db_filename = self.db_filename

            system = platform.system()
            if system == "Windows":
                try:
                    document_path = os.path.expanduser('~/Documents')
                    if os.path.exists(document_path) and os.access(document_path, os.W_OK):
                        base_path = document_path
                    else:
                        raise OSError("Docemnts folder is not accessible.")
                except OSError:
                    try:
                        user_profile = os.environ('USERPROFILE')
                        if user_profile:
                            base_path = os.path.join(user_profile, 'AppData', 'Roaming')
                        else:
                            base_path = os.path.expanduser('~\\AppData\\Roaming')

                        if not os.access(base_path, os.W_OK):
                            raise OSError("AppData folder is not ediatable")
                    except OSError:
                        # Fallback to current working
                        return os.path.join(os.getcwd(), db_filename)
                    
            elif system == "Darwin":
                base_path = os.path.expanduser('~/Library/Application Support')
            else:
                base_path = os.environ.get('XDG_DATA_HOME')
                if not base_path:
                    base_path = os.path.expanduser('~/.local/share')

            app_data_directory = os.path.join(base_path, app_name)

            try:
                os.makedirs(app_data_directory, exist_ok=True)
                test_file = os.path.join(app_data_directory, '.write_test')
                with open(test_file, 'w') as f:
                    f.write('test')
                
                os.remove(test_file)  
            except OSError:
                return os.path.join(os.getcwd(), db_filename)
            
            return os.path.join(app_data_directory, db_filename)

    def _initialize_database(self):
        """Create tables and initial salt row when missing."""
        try:
            with sqlite3.connect(self.DB_PATH) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS secrets (
                        id INTEGER PRIMARY KEY,
                        encryption_salt TEXT NOT NULL
                    )
                ''')

                cursor.execute("SELECT encryption_salt FROM secrets WHERE id = 1")
                if not cursor.fetchone():
                    import os, base64
                    new_salt = os.urandom(16)
                    cursor.execute(
                        "INSERT INTO secrets (id, encryption_salt) VALUES (1, ?)",
                        (base64.b64encode(new_salt).decode(),)
                    )

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS master_password (
                        id INTEGER PRIMARY KEY,
                        password_hash BLOB NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS passwords (
                        id INTEGER PRIMARY KEY,
                        website TEXT NOT NULL,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP    
                    )
                ''')

                connection.commit()
        except sqlite3.Error:
            pass

    # Master password storage
    def get_master_hash(self):
        try:
            with sqlite3.connect(self.DB_PATH) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT password_hash FROM master_password WHERE id = 1")
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error:
            return None

    def set_master_hash(self, hash_bytes):
        try:
            with sqlite3.connect(self.DB_PATH) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO master_password (id, password_hash) VALUES (1, ?)",
                    (hash_bytes,)
                )

                connection.commit()
                return True
        except sqlite3.Error:
            return False

    # Salt storage
    def get_encryption_salt(self):
        try:
            with sqlite3.connect(self.DB_PATH) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT encryption_salt FROM secrets WHERE id = 1")
                row = cursor.fetchone()
                if not row:
                    return None
                return base64.decode(row[0].encode())
        except sqlite3.Error:
            return None

    # Password CRUD
    def fetch_passwords_meta(self):
        try:
            with sqlite3.connect(self.DB_PATH) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT id, website, username, created_at FROM passwords ORDER BY created_at DESC")
                return cursor.fetchall()
        except sqlite3.Error:
            return []
        
    def fetch_passwords_by_id(self, pw_id):
        try:
            with sqlite3.connect(self.DB_PATH) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT password FROM passwords WHERE id = ?", (pw_id,))
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error:
            return []
        
    def insert_passsword(self, website, username, encrypted_password):
        try:
            with sqlite3.connect(self.DB_PATH) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)",
                    (website, username, encrypted_password)
                )
                connection.commit()
                return cursor.lastrowid
        except sqlite3.Error:
            return None
        
    def update_password(self, pw_id, username=None, encrypted_password=None):
        try:
            with sqlite3.connect(self.DB_PATH) as connection:
                cursor = connection.cursor()
                if username is not None and encrypted_password is not None:
                    cursor.execute(
                        "UPDATE passwords SET username = ?, password = ? WHERE id = ?", (username, encrypted_password, pw_id))
                elif username is not None:
                    cursor.execute("UPDATE passwords SET username = ? WHERE id = ?", (username, pw_id))
                elif encrypted_password is not None:
                    cursor.execute("UPDATE passwords SET password = ? WHERE id = ?", (encrypted_password, pw_id))
                else:
                    return False
                connection.commit()
        except sqlite3.Error:
            return False
        
    def delete_password(self, pw_id):
        try:
            with sqlite3.connect(self.DB_PATH) as connection:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM passwords WHERE id = ?", (pw_id,))
                connection.commit()
                return True
        except sqlite3.Error:
            return False
        
    def fetch_all_encrypted(self):
        try:
            with sqlite3.connect(self.DB_PATH) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT id, password FROM passwords")
                return cursor.fetchall()
        except sqlite3.Error:
            return []