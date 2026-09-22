"""Persistent Ed25519 key material for long-lived authority deployments."""
from __future__ import annotations
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from .crypto import Signer

class PersistentSigner(Signer):
    def __init__(self,path:str|Path="authority.key"):
        self.path=Path(path)
        if self.path.exists():
            key=serialization.load_pem_private_key(self.path.read_bytes(),password=None)
            if not isinstance(key,Ed25519PrivateKey): raise ValueError("authority key is not Ed25519")
            super().__init__(key)
        else:
            super().__init__()
            self.path.parent.mkdir(parents=True,exist_ok=True)
            self.path.write_bytes(self.private_key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
            try:self.path.chmod(0o600)
            except OSError:pass
