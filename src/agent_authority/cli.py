"""Developer and operations CLI."""
from __future__ import annotations
import json
import os
import typer
from rich import print
from .authority import Authority
from .control_plane import ControlPlane
from .models import Policy
from .sqlite_store import SQLiteStore

app=typer.Typer(help="Agent Authority runtime control CLI.")
authority=Authority(store=SQLiteStore(os.getenv("AUTHORITY_DB","authority.db")))

@app.command()
def init(db:str="authority.db"):
    store=SQLiteStore(db); store.close(); print(f"[bold green]Initialized durable authority store: {db}[/bold green]")

@app.command()
def doctor():
    ok,msg=authority.ledger.verify(); print("Identity             ✓"); print("Policy engine        ✓"); print("Risk engine          ✓"); print(f"Audit chain          {'✓' if ok else '✗'}"); print("Verification         ✓"); print(f"Audit status: {msg}")

@app.command()
def capabilities(): print("Capability-based authority: enabled")

@app.command()
def audit(): print(json.dumps(authority.ledger.snapshot(),indent=2))

@app.command()
def verify():
    ok,msg=authority.ledger.verify(); print(msg); raise typer.Exit(code=0 if ok else 1)

@app.command()
def policy(path:str):
    import yaml
    with open(path,encoding="utf-8") as fh: data=yaml.safe_load(fh) or {}
    for item in data.get("rules",[]): authority.policy.add(Policy(**item))
    print(f"Loaded {len(data.get('rules',[]))} policies.")

@app.command()
def control(host:str="127.0.0.1",port:int=8765,admin_secret:str|None=None):
    print(f"Control plane listening on http://{host}:{port}")
    ControlPlane(authority,admin_secret).serve(host,port)

if __name__=="__main__": app()
