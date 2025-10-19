import bcrypt
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

class CryptoManager:
    def __init__(self, storage):
        self.storage = storage
        self.fernet = None

    def hash_master_password(self, password: str) -> bytes:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.storage.set_master_hash(hashed)
        return hashed
    
    def verify_master_password(self, attempt: str) -> bool:
        stored = self.storage.get_master_hash()
        if not stored:
            return False
        try:
            return bcrypt.checkpw(attempt.encode('utf-8'), stored)
        except Exception:
            return False
        
    def dervive_key(self, password: str) -> bytes:
        salt = self.storage.get_encryption_salt()
        if not salt:
            raise RuntimeError("Encryption salt not found in storage.")
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600_000,
        )

        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def create_fernet(self, password: str):
        key = self.dervive_key(password)
        self.fernet = Fernet(key)

        return self.fernet
    
    def encrypt(self, plaintext: str) -> str:
        if not self.fernet:
            raise RuntimeError("Fernet instance not initialized.")
        
        token = self.fernet.encrypt(plaintext.encode())
        return base64.b64decode(token).decode('utf-8')

    def decrypt(self, token_b64: str) -> str:
        if not self.fernet:
            raise RuntimeError("Fernet instance not initialized.")
        
        token = self.fernet.decrypt(token_b64.encode('utf-8'))
        return self.fernet.decrypt(token).decode('utf-8')