import os
import json
import base64
from dataclasses import dataclass
from typing import Dict, Any

from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


@dataclass
class KdfParams:
    time_cost: int = 3
    memory_cost: int = 65536  #(64 MB)
    parallelism: int = 2
    hash_len: int = 32

# Derive a secret key from the master password using Argon2id
def derive_key_from_master(master_password: str, salt: bytes, params: KdfParams) -> bytes:

    return hash_secret_raw(
        secret=master_password.encode("utf-8"),
        salt=salt,
        time_cost=params.time_cost,
        memory_cost=params.memory_cost,
        parallelism=params.parallelism,
        hash_len=params.hash_len,
        type=Type.ID,
    )
# Encrypt a Python dict into an envolope ready to be saved to disk
def encrypt_vault(master_password: str, plain_data: Dict[str, Any]) -> Dict[str, Any]:

    kdf_params = KdfParams()
    salt = os.urandom(16)
    key = derive_key_from_master(master_password, salt, kdf_params)

    aesgcm = AESGCM(key)
    nonce = os.urandom(12)

    plaintext = json.dumps(plain_data, ensure_ascii=False).encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)

    envelope = {
        "version": 1,
        "kdf": {
            "name": "argon2id",
            "salt": base64.b64encode(salt).decode("utf-8"),
            "time": kdf_params.time_cost,
            "memory": kdf_params.memory_cost,
            "parallelism": kdf_params.parallelism,
            "length": kdf_params.hash_len,
        },
        "cipher": {
            "name": "AES-GCM",
            "nonce": base64.b64encode(nonce).decode("utf-8"),
        },
        "data": base64.b64encode(ciphertext).decode("utf-8"),
    }

    return envelope


# Decrypt an envelope (loaded from disck) into the original Python dict.
# Raises an exception if the password is wrong or data is corrupted.
def decrypt_vault(master_password: str, envelope: Dict[str, Any]) -> Dict[str, Any]:

    kdf_info = envelope["kdf"]
    cipher_info = envelope["cipher"]

    salt = base64.b64decode(kdf_info["salt"])
    nonce = base64.b64decode(cipher_info["nonce"])
    ciphertext = base64.b64decode(envelope["data"])

    kdf_params = KdfParams(
        time_cost=kdf_info["time"],
        memory_cost=kdf_info["memory"],
        parallelism=kdf_info["parallelism"],
        hash_len=kdf_info["length"],
    )

    key = derive_key_from_master(master_password, salt, kdf_params)
    aesgcm = AESGCM(key)

    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    data = json.loads(plaintext.decode("utf-8"))

    return data


