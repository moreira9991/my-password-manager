<p align="center">
  <img src="assets/logo.png" width="800">
</p>


# Password Manager – Python & Tkinter  
A lightweight, secure, and fully encrypted password manager built with Python and Tkinter.  
All stored credentials are protected using industry-standard AES-GCM encryption with a key derived from your master password using Argon2id.

This project serves as a demonstration of strong software architecture, GUI development, and secure data handling.


## Features

### Security
- **Fully encrypted storage (AES-GCM)**  
  All passwords are stored only inside an encrypted `vault.pmdb` file.
- **Argon2id key derivation**  
  The master password is never stored. Instead, it is used to derive an encryption key using Argon2id.
- **Strong master password enforcement**  
  Password strength is analyzed using *zxcvbn*.
- **Vault re-encryption on master password change**
- **Zero plaintext storage on disk**

### GUI (Tkinter)
- Add, edit, or delete saved accounts  
- Smooth scrolling for large lists  
- Search accounts by website  
- Show/Hide password visibility (double-click or button)  
- First-run setup for creating a master password  
- Secure confirmation dialogs  
- Required master password validation before sensitive actions

### Other
- Password generator (strong random passwords)
- Modular and clean architecture  
- Encrypted email backup (optional, configurable via Brevo, see [Backup Setup](docs/backup.md))



## Tech Stack

- **Python 3.10+**
- **Tkinter** (GUI)
- **cryptography** (AES-GCM)
- **argon2-cffi** (Argon2id KDF)
- **zxcvbn** (password strength analysis)
- **requests** (HTTP client for external APIs)
- **JSON** (internal representation before encryption)
- **Brevo API** (optional, for encrypted email backups)



## Project Structure
```yaml
.
├── main.py
├── app/
│ ├── gui.py # Tkinter windows / UI logic
│ ├── service.py # Service (AccountService)
│ ├── crypto_vault.py # Encryption / decryption (AES-GCM + Argon2id)
│ ├── encrypted_store.py # EncryptedStore (vault handling)
│ └── email_service.py # Send email with backup file + instructions attached
└── vault.pmdb # Encrypted vault (ignored in Git)
```



## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/password-manager.git
cd password-manager
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate     # Linux/Mac
# or
.venv\Scripts\activate        # Windows

```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Launch the app
```bash
python main.py
```

### **Linux users**: make sure python3-tk is installed.

## Backup Feature

My Password Manager includes an optional **encrypted backup** feature that allows you to:

- Create a timestamped encrypted backup of your `vault.pmdb`
- Package it into a `.zip` file together with usage instructions
- Send the backup by email using Brevo’s transactional API
 
If you want to enable the backup feature, follow the step-by-step guide in [`docs/backup.md`](docs/backup.md).


## Encryption Details
All saved passwords are stored only inside an encrypted file called `vault.pmdb`.  
This file is useless on its own — it can only be opened with the correct master password.

Behind the scenes, two main building blocks are used:

- **Argon2id** – takes your master password and turns it into a strong encryption key.  
  It is designed to be slow and memory-hard, which makes large-scale cracking attacks much harder.

- **AES-GCM (256-bit)** – uses that key to encrypt and decrypt the vault.  
  This mode provides both confidentiality (hides the data) and integrity (detects tampering).

Internal workflow:
```
master password
      ↓
Argon2id → key
      ↓
AES-GCM → encrypted vault
```
Without the correct master password, recovering vault data is computationally impractical.


## Screenshots

<p align="center">
  <img src="assets/screenshots/login_screen.png" width="650">
</p>
<p align="center"><em>Login screen — after providing the correct password, the user is granted access to the main application.</em></p>

<br>

<p align="center">
  <img src="assets/screenshots/main_window.png" width="650">
</p>
<p align="center"><em>Main window — add accounts, generate passwords, and navigate the app.</em></p>

<br>

<p align="center">
  <img src="assets/screenshots/saving_account.png" width="650">
</p>
<p align="center"><em>Creating account — add website, username, and password with strength validation.</em></p>

<br>

<p align="center">
  <img src="assets/screenshots/my_password_window.png" width="650">
</p>
<p align="center"><em>My Passwords — scrollable list of stored accounts with hidden passwords.</em></p>

<br>

<p align="center">
  <img src="assets/screenshots/filter_website.png" width="650">
</p>
<p align="center"><em>Filter website — search passwords associated with a specific platform.</em></p>

<br>

<p align="center">
  <img src="assets/screenshots/edit_or_delete_acc.png" width="650">
</p>
<p align="center"><em>Edit/Delete — manage existing accounts with confirmation dialogs.</em></p>

<br>

<p align="center">
  <img src="assets/screenshots/security_check_before_managing_master_password.png" width="650">
</p>
<p align="center"><em>Security check — re-enter the master password before sensitive operations.</em></p>

<br>

<p align="center">
  <img src="assets/screenshots/manage_master_password.png" width="650">
</p>
<p align="center"><em>Manage Master Password — update the master password with strength validation.</em></p>

 
## Coming Soon
- **Session will close automatically after inactivity**


## Disclaimer
This application is a personal learning project and not intended for professional use in production environments.
Although strong cryptographic techniques are implemented, no formal security audit has been performed.

## License
MIT License — free for personal and educational use.

## About the Author
Developed by Guilherme Moreira as part of a personal journey in Python development, cryptography, and secure application design.