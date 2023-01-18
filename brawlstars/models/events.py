from .utils import parse_battleTime, Base
from ..enums import EventMode


class ScheduledEvent:
    __slots__ = ("id", "event", "startTime", "endTime")

    def __init__(self, data: dict) -> None:
        self.id:int = data.get("slotId")
        self.event = Event(data.get("event"))
        self.startTime = parse_battleTime(data.get("startTime"))
        self.endTime = parse_battleTime(data.get("endTime"))

    def total_event_time(self):
        """returns the total event time (end-start)"""
        return self.endTime - self.startTime


ScheduledEvents = list[ScheduledEvent]


class Event(Base):
    __slots__ = ("id", "map", "mode")

    def __init__(self, data: dict) -> None:
        self.id: int = data.get("id")
        self.mode: EventMode = data.get("mode")
        self.map: str = data.get("map")
