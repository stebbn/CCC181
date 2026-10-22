from dataclasses import dataclass
from typing import TypedDict, Literal

type status_types = Literal["waiting", "processing", "none", "completed"]

@dataclass
class Item:
    name: str
    count: int

    info: str

@dataclass
class Ticket:
    number: int

    """
    must be user name
    """
    name: str
    items: list[Item] | None

    service_id: int
    status: status_types

class ServiceDict(TypedDict):
    id: int
    name: str

type TicketTable = list[Ticket]