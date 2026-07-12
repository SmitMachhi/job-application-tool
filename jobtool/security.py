from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptedStore:
    def __init__(self, path: Path, password: str):
        self.path = path
        self.password = password

    def save_json(self, payload: dict[str, Any]) -> None:
        salt = os.urandom(16)
        token = self._fernet(self.password, salt).encrypt(json.dumps(payload).encode("utf-8"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(b"JOBTOOL1" + salt + token)

    def load_json(self, password: str | None = None) -> dict[str, Any]:
        raw = self.path.read_bytes()
        if not raw.startswith(b"JOBTOOL1"):
            raise ValueError("Unsupported encrypted profile format")
        salt = raw[8:24]
        token = raw[24:]
        try:
            data = self._fernet(password or self.password, salt).decrypt(token)
        except InvalidToken as exc:
            raise ValueError("Wrong password or corrupted encrypted profile") from exc
        return json.loads(data.decode("utf-8"))

    @staticmethod
    def _fernet(password: str, salt: bytes) -> Fernet:
        if not password:
            raise ValueError("Password is required for encrypted storage")
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000)
        key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
        return Fernet(key)
