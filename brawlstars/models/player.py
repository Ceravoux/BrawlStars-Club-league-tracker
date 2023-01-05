from .brawler import BrawlerStatList, BrawlerStat
from .utils import Base

class PlayerClub(Base):
    __slots__ = ("tag", "name")
    def __init__(self, data) -> None:
        self.tag = data.get("tag")
        self.name = data.get("name")


class PlayerIcon(Base):
    __slots__ = ("id",)
    def __init__(self, data) -> None:
        self.id = data.get("id")


class Player(Base):
    __slots__ = (
        "tag",
        "name",
        "club",
        "isQualifiedFromChampionshipChallenge",
        "_3vs3Victories",
        "icon",
        "trophies",
        "expLevel",
        "expPoints",
        "highestTrophies",
        "powerPlayPoints",
        "highestPowerPlayPoints",
        "soloVictories",
        "duoVictories",
        "bestRoboRumbleTime",
        "bestTimeAsBigBrawler",
        "brawlers",
        "nameColor",
    )

    def __init__(self, data: dict) -> None:
        self.tag = data.get("tag")
        self.name = data.get("name")
        self.club: PlayerClub = PlayerClub(data.get("club"))
        self.isQualifiedFromChampionshipChallenge: bool = data.get("isQualifiedFromChampionshipChallenge")
        self._3vs3Victories: int = data.get("3vs3Victories")
        self.icon: PlayerIcon = PlayerIcon(data.get("icon"))
        self.trophies: int = data.get("trophies")
        self.expLevel: int = data.get("expLevel")
        self.expPoints: int = data.get("expPoints")
        self.highestTrophies: int = data.get("highestTrophies")
        self.powerPlayPoints: int = data.get("powerPlayPoints")
        self.highestPowerPlayPoints: int = data.get("highestPowerPlayPoints")
        self.soloVictories: int = data.get("soloVictories")
        self.duoVictories: int = data.get("duoVictories")
        self.bestRoboRumbleTime: int = data.get("bestRoboRumbleTime")
        self.bestTimeAsBigBrawler: int = data.get("bestTimeAsBigBrawler")
        self.brawlers: BrawlerStatList = [BrawlerStat(i) for i in data.get("brawlers", [])]
        self.nameColor: str = data.get("nameColor")

    def is_club_member(self, clubtag:str):
        if isinstance(clubtag, str):
            return self.club.tag == clubtag
        raise ValueError()