"""Cryptographic primitives for authority tokens and audit chains."""
from __future__ import annotations
import base64
import hashlib
import json
import secrets
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def canonical_json(value:object)->bytes: return json.dumps(value,sort_keys=True,separators=(",",":"),default=str).encode()
def sha256(value:object)->str: return hashlib.sha256(canonical_json(value)).hexdigest()
class Signer:
    def __init__(self,private_key:Ed25519PrivateKey|None=None): self.private_key=private_key or Ed25519PrivateKey.generate(); self.public_key=self.private_key.public_key()
    def sign(self,payload:object)->str: return base64.urlsafe_b64encode(self.private_key.sign(canonical_json(payload))).decode()
    def verify(self,payload:object,signature:str)->bool:
        try: self.public_key.verify(base64.urlsafe_b64decode(signature.encode()),canonical_json(payload)); return True
        except (InvalidSignature,ValueError): return False
def random_id(prefix:str)->str: return f"{prefix}-{secrets.token_hex(8)}"
