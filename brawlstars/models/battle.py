from typing import TypeVar
from .utils import parse_battleTime, Base
from .events import Event

class TeamPlayer(Base):
    __slots__ = ("tag", "name", "brawler")

    def __init__(self, data: dict) -> None:
        self.tag: str = data.get("tag")
        self.name: str = data.get("name")
        self.brawler: BrawlerInfo = BrawlerInfo(data.get("brawler", {}))


Team = TypeVar("Team", bound=list[TeamPlayer])


class BrawlerInfo(Base):
    __slots__ = ("id", "name", "power", "trophies")

    def __init__(self, data: dict) -> None:
        self.id: int = data.get("id")
        self.name: str = data.get("name")
        self.power: int = data.get("power")
        self.trophies: int = data.get("trophies")


starPlayer = TeamPlayer


class BattleResult(Base):
    __slots__ = (
        "mode",
        "type",
        "result",
        "duration",
        "starPlayer",
        "teams",
        "players",
        "trophyChange",
    )

    def __init__(self, data: dict) -> None:
        self.mode: str = data.get("mode")
        self.type: str = data.get("type", "Event")
        self.result: str = data.get("result")
        self.duration: int = data.get("duration")
        self.starPlayer: starPlayer = (
            TeamPlayer(data.get("starPlayer")) if data.get("starPlayer") else None
        )
        self.players = [TeamPlayer(i) for i in data.get("players", [])]
        self.teams: list[Team] = [self.__create_team(i) for i in data.get("teams", [])]

        # if type ranked | teamRanked:
        self.trophyChange: int = data.get("trophyChange", 0)


    @staticmethod
    def __create_team(team):
        return [TeamPlayer(player) for player in team]

    def is_friendly(self):
        return self.type == "friendly"

    def is_regular_CL_team(self):
        if self.duration is not None and (
            (self.trophyChange == 4 and self.result == "victory")
            or (self.trophyChange == 3 and self.result == "draw")
            or (self.trophyChange == 2 and self.result == "lose")
        ):
            return True

    def is_regular_CL_random(self):
        if self.duration is not None and (
            (self.trophyChange == 3 and self.result == "victory")
            or (self.trophyChange == 2 and self.result == "draw")
            or (self.trophyChange == 1 and self.result == "lose")
        ):
            return True

    def is_power_match_CL_team(self):
        return self.type == "teamRanked" and self.trophyChange in (5, 9)

    def is_power_match_CL_random(self):
        return self.type == "teamRanked" and self.trophyChange in (3, 7)

    def is_power_league_team(self):
        return (
            self.type == "teamRanked"
            and self.starPlayer is not None
            and self.trophyChange == 0
        )

    def is_power_league_solo(self):
        return (
            self.type == "soloRanked"
            and self.starPlayer is not None
            and self.trophyChange == 0
        )


class Battle(Base):
    __slots__ = ("battleTime", "event", "battle")

    def __init__(self, data: dict) -> None:
        self.battleTime = parse_battleTime(data.get("battleTime"))
        self.event: Event = Event(data.get("event"))
        self.battle: BattleResult = BattleResult(data.get("battle"))

    @property
    def trophyChange(self):
        return self.battle.trophyChange

    @property
    def teams(self):
        return self.battle.teams

    @property
    def players(self):
        return self.battle.players

    @property
    def result(self):
        return self.battle.result

    @property
    def type(self):
        return self.battle.type

    def is_friendly(self):
        return self.battle.is_friendly()

    def is_regular_CL_team(self):
        return self.battle.is_regular_CL_team()

    def is_regular_CL_random(self):
        return self.battle.is_regular_CL_random()

    def is_power_match_CL_team(self):
        return self.battle.is_power_match_CL_team()

    def is_power_match_CL_random(self):
        return self.battle.is_power_match_CL_random()

    def is_power_league(self):
        return self.battle.is_power_league_solo() or self.battle.is_power_league_team()



