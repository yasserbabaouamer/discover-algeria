from dataclasses import dataclass


@dataclass
class GuestTokens:
    access: str
    refresh: str
    has_guest_acc: bool
