import json
from pathlib import Path
from typing import Any
from app.crypto_vault import encrypt_vault, decrypt_vault
from datetime import datetime
import shutil
# Raised when decryption fails due to wrong password or corrupted file
class VaultDecryptionError(Exception):
    pass

# Encrypt vault store.
# In memory: {site_key:{"username":str,"password":str},...}
# On disk: encrypted envelope created by encrypt_vault()
class EncryptedStore:
    def __init__(self, path: Path | str = "vault.pmdb") -> None:
        self.path = Path(path)
        self.backup_path = Path("backup/")

    def _load_envelope(self) -> dict[str, Any]:
        if not self.path.exists():
            raise FileNotFoundError(f"Vault file not found: {self.path}")
        try:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse vault file: {e}") from e

    def _save_envelope(self, envelope: dict[str, Any]) -> None:
        if self.path.parent and not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(envelope, f, indent=4, ensure_ascii=False)


    # Load and decrypt the vault
    # If file does not exists creates empty vault with new master password
    # If exists, try to decrypt with master password provided
    def load(self, master_password: str) -> dict[str, Any]:
  
        # First run: no vault yet
        if not self.path.exists():
            data: dict[str, Any] = {}
            envelope = encrypt_vault(master_password, data)
            self._save_envelope(envelope)
            return data

        # Vault exists: read + decrypt
        envelope = self._load_envelope()
        try:
            data = decrypt_vault(master_password, envelope)
            if not isinstance(data, dict):
                raise RuntimeError("Decrypted vault is not a dictionary.")
            return data
        except Exception as e:
            raise VaultDecryptionError(
                "Failed to decrypt vault. Wrong password or corrupted file."
            ) from e


    # Encrypt and save the given data dict using the provided master password
    def save(self, master_password: str, data: dict[str, Any]) -> None:

        envelope = encrypt_vault(master_password, data)
        self._save_envelope(envelope)

    # Creates a backup vault with time stamp of its creation.
    def create_backup_vault(self) -> Path:
        self.backup_path.mkdir(parents=True,exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_path / f"vault_backup_{timestamp}{self.path.suffix}"

        shutil.copy2(self.path,backup_file)
        return backup_file