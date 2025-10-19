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
        self.DB_PATH = self
        self._initialize_database()

        def _get_app_data_directory(self):
            """Get platform-appropriate database path for the appliaction"""

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
        
