import time
from rich.console import Console
from rich.table import Table

from .database import DatabaseManager
from .ui import UIManager
from .crypto import CryptoManager
from .utils import generate_password, check_complexity

class Server:
    def __init__(self):
        self.console = Console()
        self.database = DatabaseManager()
        self.crypto = CryptoManager()
        self.ui = UIManager()
        self.is_authenticated = False
        self.fernet = None
        self.most_recent_id = None


    def _check_master_password_exist(self):
        return True if self.storage.get_master_hash() else False
        
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

            if choice in ("/choice", "/c"):
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
            print("No password found for the given ID: {id}\n")
            return
        try:
            dec = self.crypto.decrypt(enc)
            self.console.preint(f"Decrypted password: [bold]{dec}[/bold]")
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
                    self.console.print(f"Generated passord for the {website}: {pwd}", style="green")
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
        