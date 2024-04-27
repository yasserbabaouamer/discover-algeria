from dataclasses import dataclass


@dataclass
class OwnerTokens:
    access: str
    refresh: str
    has_owner_acc: bool
