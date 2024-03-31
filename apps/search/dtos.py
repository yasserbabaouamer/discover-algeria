from dataclasses import dataclass


@dataclass
class SearchItem:
    id: int
    type: str
    image: str
    name: str
    address: str
    relevance: float
