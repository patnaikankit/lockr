# Lockr - Secure Password Manager

A secure, command-line based password manager built in Python that helps you store and manage your passwords safely with strong encryption.


## Features

- 🔐 **Secure Password Storage**: All passwords are encrypted using Fernet symmetric encryption
- 🔑 **Master Password Protection**: Single master password to secure all your stored passwords
- 🎯 **Easy-to-Use CLI**: Simple command-line interface with intuitive commands
- 📋 **Clipboard Integration**: Quick password copying to clipboard
- 🔄 **Password Management**: Add, view, update, and delete passwords
- 🔒 **Strong Encryption**: Uses PBKDF2-HMAC-SHA256 for key derivation
- 📱 **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

```bash
git clone https://github.com/patnaikankit/lockr.git

cd lockr

uv sync
```

## Quick Start

1. Run the password manager:
```bash
python -m lockr
```
or

If you are on Windows run
```
.\lockr.bat
```

2. Set up your master password when prompted on first run
3. Use the available commands to manage your passwords

## Commands

| Command | Shortcut | Description |
|---------|----------|-------------|
| /help   | /h       | Show all commands |
| /info   | /i       | Show version details |
| /view   | /v       | View stored passwords |
| /add    | /a       | Add a new password |
| /update | /u       | Update existing password |
| /delete | /d       | Delete a password |
| /copy   | /c       | Copy password to clipboard |
| /master | /m       | Change master password |
| /quit   | /q       | Exit the program |

## Security Features

- Uses Fernet (symmetric encryption) for password encryption
- PBKDF2-HMAC-SHA256 for key derivation with 600,000 iterations
- Secure storage of master password using bcrypt
- Automatic clipboard clearing
- No plaintext password storage

## Data Storage

The password database is stored securely in your system's app data directory:
- Windows: `~/Documents/lockr/lockr.db`
- macOS: `~/Library/Application Support/lockr/lockr.db`
- Linux: `~/.local/share/lockr/lockr.db`

## Development

The project is structured as follows:
```
lockr/
├── src/
│   └── lockr/
│       ├── __init__.py
│       ├── crypto.py      # Encryption/decryption logic
│       ├── database.py    # Database management
│       ├── main.py        # Entry point
│       ├── manager.py     # Core password management
        ├── utils.py       # Helper functions
│       └── ui.py          # User interface
├── LICENSE
├── README.md
└── pyproject.toml
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
