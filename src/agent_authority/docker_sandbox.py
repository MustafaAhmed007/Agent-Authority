"""Concrete Docker isolation adapter.

Requires a locally available Docker daemon. The adapter intentionally uses
allow-listed arguments and never interpolates a shell command.
"""
from __future__ import annotations
import subprocess
from dataclasses import dataclass

@dataclass(frozen=True)
class DockerSandboxConfig:
    image: str = "python:3.11-slim"
    network: str = "none"
    memory: str = "512m"
    cpus: str = "1.0"
    pids_limit: str = "128"
    read_only: bool = True
    timeout_seconds: int = 30

class DockerSandbox:
    def __init__(self, config: DockerSandboxConfig | None = None):
        self.config = config or DockerSandboxConfig()

    def run(self, argv: list[str], workdir: str | None = None) -> subprocess.CompletedProcess[str]:
        if not argv or any("\x00" in x for x in argv):
            raise ValueError("invalid sandbox command")
        c = self.config
        cmd = ["docker", "run", "--rm", "--network", c.network, "--memory", c.memory,
               "--cpus", c.cpus, "--pids-limit", c.pids_limit, "--cap-drop", "ALL",
               "--security-opt", "no-new-privileges:true"]
        if c.read_only:
            cmd += ["--read-only", "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m"]
        if workdir:
            cmd += ["--workdir", "/workspace", "--mount", f"type=bind,src={workdir},dst=/workspace,readonly"]
        cmd += [c.image, *argv]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=c.timeout_seconds, check=False)
