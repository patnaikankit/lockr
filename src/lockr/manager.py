import time
import pyperclip
from rich.console import Console
from rich.table import Table

from .database import DatabaseManager
from .ui import UIManager
from .crypto import CryptoManager
from .utils import generate_password, check_complexity

class Server:
    def __init__(self):
        self.version = "1.0.0"
        self.console = Console()
        self.database = DatabaseManager()
        self.crypto = CryptoManager(self.database)
        self.ui = UIManager()
        self.is_authenticated = False
        self.fernet = None
        self.most_recent_id = None


    def _check_master_password_exist(self):
        return True if self.database.get_master_hash() else False
        
    def authenticate(self):
        while not self.is_authenticated:
            attempt = self.console.input("[yellow]> [/yellow]Enter master password: ").strip()
            if attempt in ("/quit", "/q"):
                print("Exiting...")
                raise SystemExit()
            if self.crypto.verify_master_password(attempt):
                self.crypto.create_fernet(attempt)
                self.is_authenticated = True
                self.console.print("Authentication successful!", style="green")
            else:
                self.console.print("Incorrect master password. Access denied.", style="red")
                print("Please try again or type /quit to exit.")
            
    def create_master_password(self):
        while True:
            choice = self.console.input("[yellow]> [/yellow]Choose master password method - /create to type your own, /generate for a random one: ").strip()

            if choice in ("/create", "/c"):
                while True:
                    pwd = self.console.input("[yellow]> [/yellow]Create master password: ").strip()
                    ok, reqs = check_complexity(pwd)
                    if ok:
                        break
                    else:
                        self.console.print(f"Password must contain: {', '.join(reqs)}", style="red")
                break
            elif choice in ("/generate", "/g"):
                while True:
                    length = self.console.input("[yellow]> [/yellow]Enter password length (min 16): ").strip()

                    if not length.isdigit():
                        print("Please enter a valid number.")

                    if int(length) < 16:
                        print("Password must have atleast 16 characters.")
                        continue

                    pwd = generate_password(int(length))
                    self.console.print(f"Generated master password: [bold]{pwd}[/bold]\n", style="green")
                    self.console.print("Please store it securely as it cannot be recovered later.\n", style="red")
                    break
                break
            else:
                self.console.print("Invalid input. Enter '/create' or '/generate'", style="red")

        time.sleep(10)

        # hash & store
        self.crypto.hash_master_password(pwd)
        self.crypto.create_fernet(pwd)
        self.is_authenticated = True

    def _validate_input(self, value, field_name):
        if not value or not value.strip():
            self.console.print(f"{field_name} cannot be empty.", style="red")
            return False
        return True

    def handle_view(self):
        entries = self.database.fetch_passwords_meta()
        if not entries:
            self.console.print("No passwords found.", style="yellow")
            return 
        
        table = Table(title="\nStored password entries")
        table.add_column("ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Website", justify="center", style="cyan", no_wrap=True)
        table.add_column("Username", justify="center", style="cyan", no_wrap=True)
        table.add_column("Creation Date", justify="center", style="cyan", no_wrap=True)

        for entry in entries:
            table.add_row(f"{entry[0]}", f"{entry[1]}", f"{entry[2]}", f"{entry[3]}")
        self.console.print(table)
        print("")

        id = self.console.input("[yellow]> [/yellow]Enter the ID of the password you want to view: ").strip()
        if not self._validate_input(id, "ID"):
            print("")
            return
        enc = self.database.fetch_passwords_by_id(id)
        if not enc:
            print(f"No password found for the given ID: {id}\n")
            return
        try:
            dec = self.crypto.decrypt(enc)
            self.console.print(f"Decrypted password: [bold]{dec}[/bold]")
            self.most_recent_id = id
        except Exception:
            self.console.print("Decryption failed.\n", style="red")

    def handle_add(self):
        while True:
            website = self.console.input("[yellow]> [/yellow]Enter website: ").strip()
            if self._validate_input(website, "Website"):
                break
        while True:
            username = self.console.input("[yellow]> [/yellow]Enter username: ").strip()
            if self._validate_input(username, "Username"):
                break
        while True:
            choice = self.console.input("[yellow]> [/yellow]Choose password method - /create to type your own, /generate for a random one: ").strip()
            if choice in ("/create", "/c"):
                while True:
                    pwd = self.console.input("[yellow]> [/yellow] Create pasword: ").strip()
                    ok, reqs = check_complexity(pwd, min_length=12)
                    if ok:
                        break
                    else:
                        self.console.print(f"Password must contain: {', '.join(reqs)}", style="red")
                break
            elif choice in ("/generate", "/g"):
                while True:
                    length = self.console.input("[yellow]> [/yellow]Enter password length (min 16): ").strip()
                    if not length.isdigit():
                        self.console.print("Please enter a valid number.", style="red")
                    if int(length) < 16:
                        self.console.print("Password must have 16 characters", style="red")
                        continue
                    pwd = generate_password(int(length))
                    self.console.print(f"Generated passord for {website}: {pwd}", style="green")
                    break
                break
            else:
                self.console.print("Invalid input. Enter '/create' or '/generate'", style="red")

        try:
            enc = self.crypto.encrypt(pwd)
        except Exception:
            self.console.print("Encryption failed. Password not added.\n")
            return 
        
        lastest_id = self.database.insert_passsword(website, username, enc)
        self.most_recent_id = lastest_id
        self.console.print("Password added successfully!\n", style="green")

    def handle_update(self):
        entries = self.database.fetch_passwords_meta()
        if not entries:
            self.console.print("No passwords found.", style="yellow")
            return 
        
        table = Table(title="\nStored password entries")
        table.add_column("ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Website", justify="center", style="cyan", no_wrap=True)
        table.add_column("Username", justify="center", style="cyan", no_wrap=True)
        table.add_column("Creation Date", justify="center", style="cyan", no_wrap=True)
        for entry in entries:
            table.add_row(f"{entry[0]}", f"{entry[1]}", f"{entry[2]}", f"{entry[3]}")
        self.console.print(table)

        for entry in entries:
            table.add_row(f"{entry[0]}", f"{entry[1]}", f"{entry[2]}", f"{entry[3]}")
        self.console.print(table)
        print("")

        id = self.console.input("[yellow]> [/yellow]Enter the ID of the password you want to update: ").strip()
        if not self._validate_input(id, "ID"):
            print("")
            return
        isExists = self.database.fetch_passwords_by_id(id)
        if not isExists:
            self.console.print("No password found for the given ID: {id}\n", style="red")
            return 
        
        while True:
            udec = self.console.input("[yellow]> [/yellow]Do you want to update the username? (yes/no): ").strip()
            if udec == "yes":
                while True:
                    new_username = self.console.input(f"[yellow]> [/yellow]Enter new username: ").strip()
                    if self._validate_input(new_username, "Username"):
                        self.database.update_password(id, username=new_username)
                        print("Username updated successfully.")
                        break
                break
            elif udec == "no":
                break
            else:
                self.console.print("Invalid input. Enter 'yes' or 'no' to update username.", style="red")

        while True:
            pdec = self.console.input("[yellow]> [/yellow]Do you want to update the password? (yes/no): ").strip()
            if pdec == "yes":
                while True:
                    choice = self.console.input("[yellow]> [/yellow]Choose password method - /create to type your own, /generate for a random one: ").strip()
                    if choice in ("/create", "/c"):
                        while True:
                            new_pwd = self.console.input("[yellow]> [/yellow]Create password: ").strip()
                            ok, reqs = check_complexity(new_pwd, min_length=12)
                            if ok:
                                break
                            else:
                                self.console.print(f"Password must contain: {', '.join(reqs)}", style="red")
                        break
                    elif choice in ("/generate", "/g"):
                        while True:
                            length = self.console.input("[yellow]> [/yellow]Enter password length (min 16): ").strip()
                            if not length.isdigit():
                                print("Password must be an integer.")
                                continue
                            if int(length) < 16:
                                print("Password must be atleast 16 characters.")
                                continue
                            new_pwd = generate_password(int(length))
                            print(f"This is the generated password: {new_pwd}")
                            break
                        break
                    else:
                        self.console.print("Invalid input. Enter '/create' or '/generate'", style="red")
                enc = self.crypto.encrypt(new_pwd)
                self.database.update_password(id, encrypted_password=enc)
                print("Password updated successfully")
                break
            elif pdec == "no":
                break
            else:
                self.console.print("Invalid input. Enter 'yes' or 'no' to update password.", style="red")

        self.most_recent_id = id
        print(f"Update for ID {id} complete.\n")

    def handle_delete(self):
        entries = self.database.fetch_passwords_meta()
        if not entries:
            print("No passwords stored yet.\n")
            return
        table = Table(title="\nStored password entries")
        table.add_column("ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Website", justify="center", style="cyan", no_wrap=True)
        table.add_column("Username", justify="center", style="cyan", no_wrap=True)
        table.add_column("Creation Date", justify="center", style="cyan", no_wrap=True)

        for entry in entries:
            table.add_row(f"{entry[0]}", f"{entry[1]}", f"{entry[2]}", f"{entry[3]}")
        self.console.print(table)
        print("")
        while True:
            id = self.console.input("[yellow]> [/yellow]Enter the ID of the password you want to delete: ").strip()
            if not self._validate_input(id, "ID"):
                continue

            confirm = self.console.input(f"[yellow]> [/yellow][red]Are you sure you want to delete ID: {id}? (yes/no): [/red]").strip()

            if confirm == "yes":
                meta = [m for m in entries if str(m[0]) == str(id)]
                website_name = meta[0][1] if meta else None
                success = self.database.delete_password(id)
                if success:
                    print(f"Password for website '{website_name}' (ID: {id}) has been deleted.\n")
                else:
                    print("No password found for that ID.\n")
                break
            elif confirm == "no":
                break
            else:
                self.console.print("Invalid input. 'yes' or 'no' for password deletion.", style="red")

    def handle_copy(self):
        if not self.most_recent_id:
            print("No recently viewed password to copy.\n")
        enc = self.database.fetch_passwords_by_id(self.most_recent_id)
        if not enc:
            print("Failed to copy most recent password.\n")
            return
        try:
            dec = self.crypto.decrypt(enc)
            pyperclip.copy(dec)
            self.console.print("Password copied to clipboard.", style="green")
        except Exception:
            self.console.print("Decryption failed. Cannot copy password.\n", style="red")

    def handle_master_change(self):
        # decrypt all with old fernet, collect plaintexts
        all_enc = self.database.fetch_all_encrypted()
        decrypted = []
        for pw_id, enc in all_enc:
            try:
                dec = self.crypto.decrypt(enc)
                decrypted.append((pw_id, dec))
            except Exception:
                self.console.print(f"Decryption failed for ID: {pw_id}. Skipping master password change.\n", style="red")
        
        self.create_master_password()

        # re-encrypt all with new fernet
        for pw_id, plain in decrypted:
            enc = self.crypto.encrypt(plain)
            self.database.update_password(pw_id, encrypted_password=enc)
        self.console.print("Master password changed successfully!\n", style="green")

    def run(self):
        self.console.print("Welcome to Lockr - Your Secure Password Manager\n", style="bold blue")

        if self._check_master_password_exist():
            self.authenticate()
        else:
            self.console.print("No master password found. Please create one.\n", style="yellow")
            self.create_master_password()

        if self.is_authenticated:
            self.console.clear()
            self.ui.startup_text(self.version)
            self.console.print("Access granted to password database!", style="green")

        while True:
            manager_process = self.console.input("[yellow]> [/yellow]").strip()
            if manager_process in ("/help", "/h"):
                self.ui.show_help()
            elif manager_process in ("/info", "/i"):
                self.ui.show_info(self.version)
            elif manager_process in ("/view", "/v"):
                self.handle_view()
            elif manager_process in ("/add", "/a"):
                self.handle_add()
            elif manager_process in ("/update", "/u"):
                self.handle_update()
            elif manager_process in ("/delete", "/d"):
                self.handle_delete()
            elif manager_process in ("/copy", "/c"):
                self.handle_copy()
            elif manager_process in ("/master", "/m"):
                self.handle_master_change()
            elif manager_process in ("/quit", "/q"):
                print("Goodbye, friend.")
                break
            else:
                pass