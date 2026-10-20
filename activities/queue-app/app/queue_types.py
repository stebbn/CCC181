from dataclasses import dataclass
from typing import TypedDict, Literal

type status_types = Literal["waiting", "processing", "none", "completed"]

@dataclass
class Ticket:
    number: int
    name: str
    source: str
    service_id: int
    status: status_types

class ServiceDict(TypedDict):
    id: int
    name: str

type TicketTable = list[Ticket]