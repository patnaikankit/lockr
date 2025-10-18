import string
import secrets

def generate_password(length=16) -> str:
    chars = string.ascii_letters + string.digits + string.punctuation

    return ''.join(secrets.choice(chars) for _ in range(length))

def check_complexity(password: str, min_length: int = 12):
    isValid = True
    check = []

    if len(password) < min_length:
        check.append(f"at least {min_length} characters")
        isValid = False

    if not any(c.isupper() for c in password):
        check.append("no uppercase character")
        isValid = False

    if not any(c.islower() for c in password):
        check.append("no lowercase character")
        isValid = False

    if not any(c.isdigit() for c in password):
        check.append("no digit character")
        isValid = False

    if not any(c in string.punctuation for c in password):
        check.append("no punctuation symbols")
        isValid = False

    return isValid, check 
        