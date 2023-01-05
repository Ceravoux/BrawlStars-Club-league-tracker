from datetime import datetime, timezone

class Base:
    __slots__ = ()
    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, ", ".join("{}={}".format(i, getattr(self, i, "MISSING")) for i in self.__slots__))

    __str__ = __repr__



def parse_battleTime(battleTime: str):
    assert len(battleTime) == 20 and isinstance(battleTime, str), "invalid battleTime"
    year = int(battleTime[:4])
    month = int(battleTime[4:6])
    day = int(battleTime[6:8])
    hour = int(battleTime[9:11])
    minute = int(battleTime[11:13])
    second = int(battleTime[13:15])
    return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)