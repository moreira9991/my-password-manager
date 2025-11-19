# import json
# from pathlib import Path
# from typing import Any


# class JsonStore:
#     # JSON store (no encryption).
#     # Data shape -> {site_key:{"username":str,"password":str},...}
#     def __init__(self, path: Path|str = "Passwords_data.json") -> None:
#         self.path = Path(path)

#     def load(self) -> dict[str,Any]:
#         if not self.path.exists():
#             return{}
#         try:
#             with self.path.open("r", encoding="utf-8")as f:
#                 return json.load(f)
#         except json.JSONDecodeError as e:
#             return{}
        
#     def save(self, data: dict[str,Any]) -> None:
#     # Ensure parent exists (in case you move the file later)
#         if self.path.parent and not self.path.parent.exists():
#             self.path.parent.mkdir(parents=True, exist_ok=True)
#         with self.path.open("w", encoding="utf-8") as f:
#             json.dump(data, f, indent=4, ensure_ascii=False)

import json
from pathlib import Path
from typing import Any, Dict

from app.crypto_vault import encrypt_vault, decrypt_vault


class VaultDecryptionError(Exception):
    """Raised when decryption fails (wrong password or corrupted file)."""
    pass


class EncryptedStore:
    """
    Encrypted vault store.

    In memory: {site_key: {"username": str, "password": str}, ...}
    On disk : encrypted envelope created by encrypt_vault().
    """

    def __init__(self, path: Path | str = "vault.pmdb") -> None:
        self.path = Path(path)

    def _load_envelope(self) -> Dict[str, Any]:
        if not self.path.exists():
            raise FileNotFoundError(f"Vault file not found: {self.path}")
        try:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse vault file: {e}") from e

    def _save_envelope(self, envelope: Dict[str, Any]) -> None:
        if self.path.parent and not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(envelope, f, indent=4, ensure_ascii=False)

    def load(self, master_password: str) -> dict[str, Any]:
        """
        Load and decrypt the vault.

        - If file does not exist -> create empty vault with this password.
        - If exists -> try to decrypt with this password.
        """
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

    def save(self, master_password: str, data: dict[str, Any]) -> None:
        """
        Encrypt and save the given data dict using the provided master password.
        """
        envelope = encrypt_vault(master_password, data)
        self._save_envelope(envelope)
