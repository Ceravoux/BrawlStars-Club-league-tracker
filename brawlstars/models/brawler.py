from typing import TypeVar
from .utils import Base

class Item(Base):
    """base class for `Brawler`, `Gadget`, `Gear`, and `StarPower`"""
    __slots__ = ("id", "name")

    def __init__(self, data: dict) -> None:
        self.id = data.get("id")
        self.name = data.get("name")

    def __eq__(self, other) -> bool:
        return self.id == other.id and self.name == other.name


class Brawler(Item):
    """represents a Brawler class.

    Attributes
    ----------
    id: `int`
        the brawler's id (corresponds to ..enums.BrawlerOptions)
    name: `str`
        the brawler's name.
    starPowers: `tuple[StarPower]`
        contains a tuple of starpower.
    gadgets: `tuple[Gadget]`
        contains a tuple of gadget.
    """
    __slots__ = ("starPowers", "gadgets")

    def __init__(self, data:dict) -> None:
        super().__init__(data)
        self.starPowers = tuple(StarPower(i) for i in data.get("starPowers"))
        self.gadgets = tuple(Gadget(i) for i in data.get("gadgets"))


class Gadget(Item):
    "represents a Gadget class."
    ...


GadgetList = TypeVar("GadgetList", bound=list[Gadget])


class StarPower(Item):
    "represents a StarPower class."
    ...


StarPowerList = TypeVar("StarPowerList", bound=list[StarPower])


class Gear(Item):
    "represents a Gear class."
    __slots__ = ("level",)

    def __init__(self, data:dict) -> None:
        super().__init__(data)
        self.level = data.get("level")


GearList = TypeVar("GearList", bound=list[Gear])


class BrawlerStat(Brawler):
    """Represents a brawler's stats from player's info http request."""
    __slots__ = ("rank", "trophies", "highestTrophies", "power", "gears")

    def __init__(self, data: dict) -> None:
        super().__init__(data)
        self.rank = data.get("rank")
        self.trophies = data.get("trophies")
        self.highestTrophies = data.get("highestTrophies")
        self.power = data.get("power")
        self.gears = [Gear(i) for i in data.get("gears")]


BrawlerStatList = TypeVar("BrawlerStatList", bound=list[BrawlerStat])
