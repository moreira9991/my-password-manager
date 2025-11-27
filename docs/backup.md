# Encrypted Backup Feature - Setup & Usage

This document explains how to enable and use the encrypted email backup feature of My Password Manager.

This guide assumes the application is already installed and running.
(See the main README for installation instructions.)


## 1. Requirements

Before using the backup feature, you need:

- A free **Brevo** (Sendinblue) account → https://www.brevo.com/
- A **Brevo API v3 key** (`xkeysib-...`)
- A validated **sender email** in Brevo
- Internet access
- Environment variables configured (explained below)


## 2. Create a Brevo API Key

1. Log in to your Brevo account.
2. Navigate to **SMTP & API** → **API Keys**.
3. Click **Create a new API key**.
4. Choose a name (e.g., `my-password-manager-backup`).
5. Copy the generated key.

Your API key must start with: `xkeysib-`.

**Caution!** - API keys starting with `xsmtpsib-` are SMTP keys and will **not** work here.

## 3. Configure a Sender Email in Brevo

1. Go to **Senders & Domains** in Brevo.
2. Add a sender address, for example: `youremail@gmail.com`
3. Validate the sender (Brevo sends a confirmation email).

## 4. Configure Environment Variables

The backup feature requires the following environment variables:
```md
| Variable             | Required?   | Description                        |
|----------------------|-------------|------------------------------------|
| `BREVO_API_KEY`      |    Yes      | Your Brevo API key                 |
| `BREVO_SENDER_EMAIL` | Recommended | Sender email used in backup emails |
| `BREVO_SENDER_NAME`  | Optional    | Display name for the sender        |
```

To configure these variables, do the following: 

1. In the terminal, open `~/.bashrc` or `~/.zshrc`:

```bash
nano ~/.bashrc
```

or

```bash
nano ~/.zshrc
```

2. Add these lines at the bottom of the file: 

```bash
export BREVO_API_KEY="xkeysib-XXXXXXXXXXXXXXXXXXXXXXXX"
export BREVO_SENDER_EMAIL="youremail@example.com"
export BREVO_SENDER_NAME="My Password Manager"
```

- Replace `"xkeysib-XXXXXXXXXXXXXXXXXXXXXXXX"` with your actual API key (keep it inside the quotes "").
- Replace `youremail@example.com` with the email you have validated on Brevo (keep it inside the quotes "").

To save the file in `nano`:
- Press `CTRL + O` to save
- Press Enter to confirm
- Press `CTRL + X` to exit

3. Reload:

```bash
source ~/.bashrc
```
or, if you edited `~/.zshrc`:
```bash
source ~/.zshrc
```

4. Verify:
```bash
echo $BREVO_API_KEY
echo $BREVO_SENDER_EMAIL
echo $BREVO_SENDER_NAME
```

The terminal should print the values of the variables you added.

## 5. Using the Backup Feature
1. Start the application:
```bash
python main.py
```
2. In the My Passwords window, click `Backup Passwords`.
3. Enter your **master password**.
4. Enter the **email address** where the backup should be sent.
5. Confirm the operation.

### If everything is set up correctly:
- A timestamped encrypted vault file (*.pmdb) is created.
- A backup ZIP file is generated containing:
    - the encrypted .pmdb file
    - the instructions.txt file
- The ZIP file is sent by email using Brevo.
- A success message is shown in the GUI.

If anything fails, an error message is displayed.

## 6. Restoring a Backup
1. Download the `.zip` file from your email.
2. Extract its contents.
3. Locate the `.pmdb` file.
4. Move it to the application's root directory.
5. Rename it to `vault.pmdb`.
6. Open My Password Manager.
7. Enter your master password.
8. Your vault will be restored.

## 7. Security Notes
- Never share your master password.
- Keep your backup ZIP file in a secure location.
- Do not edit the `.pmdb` file manually.
- Create new backups periodically as your data changes.