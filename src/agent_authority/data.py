"""Data classification helpers."""
from enum import IntEnum

class DataClass(IntEnum):
    PUBLIC=0; INTERNAL=1; CONFIDENTIAL=2; SENSITIVE=3; RESTRICTED=4; SECRET=5

def permits(agent_level: DataClass, data_level: DataClass) -> bool:
    return agent_level >= data_level
