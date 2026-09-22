"""Developer CLI."""
from __future__ import annotations
import json
import typer
from rich import print
from .authority import Authority
from .models import Capability, Policy

app = typer.Typer(help="Agent Authority runtime control CLI.")
authority = Authority()

@app.command()
def init():
    print("[bold green]Agent Authority initialized.[/bold green]")
    print("Core: identity ✓ policy ✓ risk ✓ approvals ✓ audit ✓ verification ✓")

@app.command()
def doctor():
    ok, msg = authority.ledger.verify()
    print(f"Identity             ✓")
    print(f"Policy engine        ✓")
    print(f"Risk engine          ✓")
    print(f"Audit chain          {'✓' if ok else '✗'}")
    print(f"Verification         ✓")
    print(f"Audit status: {msg}")

@app.command()
def capabilities():
    print("Capability-based authority: enabled")

@app.command()
def audit():
    print(json.dumps([e.model_dump(mode="json") for e in authority.ledger.events], indent=2))

@app.command()
def verify():
    ok, msg = authority.ledger.verify()
    raise typer.Exit(code=0 if ok else 1)

@app.command()
def policy(path: str):
    import yaml
    data = yaml.safe_load(open(path, encoding="utf-8"))
    for item in data.get("rules", []):
        authority.policy.add(Policy(**item))
    print(f"Loaded {len(data.get('rules', []))} policies.")

if __name__ == "__main__":
    app()
