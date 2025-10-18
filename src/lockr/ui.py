from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.align import Align

class UIManager:
    def __init__(self):
        self.console = Console()

    def startup_text(self, version: str):
        self.console.clear()
        header = Text()
        header.append("vanta", style="bold white")
        header.append("\n")
        header.append(f"v{version}", style="dim white")
        self.console.print()
        self.console.print(Align.center(header))
        self.console.print()

        table = Table(show_header=False, show_lines=False, box=None, padding=(0, 2))
        table.add_column("Command", style="dim white", width=17)
        table.add_column("Description", style="white", width=20)
        table.add_column("Shortcut", style="dim white", width=10)

        commands = [
            ("/help", "all commands", "/h"),
            ("/view", "view passwords", "/v"),
            ("/add", "add password", "/a"),
            ("/update", "update password", "/u"),
            ("/delete", "delete password", "/d"),
            ("/quit", "quit program", "/q"),
        ]
        for cmd, desc, shortcut in commands:
            table.add_row(cmd, desc, shortcut)

        self.console.print(Align.center(table))
        self.console.print()

    def show_help(self):
        table = Table(show_header=False, show_lines=False, box=None, padding=(0, 2))
        table.add_column("Command", style="dim white", width=10)
        table.add_column("Description", style="white", width=20)
        table.add_column("Shortcut", style="dim white", width=10)

        commands = [
            ("/help", "all commands", "/h"),
            ("/info", "version details", "/i"),
            ("/view", "view passwords", "/v"),
            ("/add", "add password", "/a"),
            ("/update", "update password", "/u"),
            ("/delete", "delete password", "/d"),
            ("/copy", "copy to clipboard", "/c"),
            ("/master", "change master", "/m"),
            ("/quit", "quit program", "/q"),
        ]
        for cmd, desc, shortcut in commands:
            table.add_row(cmd, desc, shortcut)

        self.console.print(table)

    def show_info(self, version: str):
        art = """
            ██      ██████   ██████ ██   ██ ██████  
            ██     ██    ██ ██      ██  ██  ██   ██ 
            ██     ██    ██ ██      █████   ██████  
            ██     ██    ██ ██      ██  ██  ██   ██    
            ██████  ██████   ██████ ██   ██ ██   ██    
            """

        self.console.print(art)
        self.console.print(f"Version: {version}", style="cyan")
        self.console.print("Repo: [link=https://github.com/eelixir/vanta]github.com/eelixir/vanta[/link]\n", style="cyan")