import tempfile
from pathlib import Path
from agent_authority import PersistentSigner

def test_persistent_signer_round_trip():
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/"authority.key"
        first=PersistentSigner(path); payload={"decision":"ALLOW","request_id":"1"}; sig=first.sign(payload)
        second=PersistentSigner(path); assert second.verify(payload,sig); assert not second.verify({"decision":"DENY"},sig)
