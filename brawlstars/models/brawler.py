from typing import TypeVar
from .utils import Base

class Item(Base):
    __slots__ = ("id", "name")

    def __init__(self, data: dict) -> None:
        self.id = data.get("id")
        self.name = data.get("name")

    def __eq__(self, other) -> bool:
        return self.id == other.id and self.name == other.name


class Brawler(Item):
    __slots__ = ("starPowers", "gadgets")

    def __init__(self, data:dict) -> None:
        super().__init__(data)
        self.starPowers = [StarPower(i) for i in data.get("starPowers")]
        self.gadgets = [Accessory(i) for i in data.get("gadgets")]


class Accessory(Item):
    ...


AccessoryList = TypeVar("AccessoryList", bound=list[Accessory])


class StarPower(Item):
    ...


StarPowerList = TypeVar("StarPowerList", bound=list[StarPower])


class GearStat(Item):
    __slots__ = ("level",)

    def __init__(self, data:dict) -> None:
        super().__init__(data)
        self.level = data.get("level")


GearStatList = TypeVar("GearStatList", bound=list[GearStat])


class BrawlerStat(Brawler):
    __slots__ = ("rank", "trophies", "highestTrophies", "power", "gears")

    def __init__(self, data: dict) -> None:
        super().__init__(data)
        self.rank = data.get("rank")
        self.trophies = data.get("trophies")
        self.highestTrophies = data.get("highestTrophies")
        self.power = data.get("power")
        self.gears = [GearStat(i) for i in data.get("gears")]


BrawlerStatList = TypeVar("BrawlerStatList", bound=list[BrawlerStat])
