from .player import PlayerIcon
from ..enums import ClubType, MemberRole
from .utils import Base

class Club(Base):
    __slots__ = (
        "tag",
        "name",
        "description",
        "requiredTrophies",
        "members",
        "type",
        "badgeId",
        "trophies"
    )

    def __init__(self, data:dict) -> None:
        self.tag: str = data.get("tag")
        self.name: str = data.get("name")
        self.description: str = data.get("description")
        self.trophies: int = data.get("trophies")
        self.requiredTrophies: int = data.get("requiredTrophies")
        self.members = data.get("members")
        self.type: ClubType = data.get("type")
        self.badgeId: int = data.get("badgeId")


class ClubMember(Base):
    __slots__ = ("tag", "name", "icon", "trophies", "role", "nameColor")

    def __init__(self, data:dict) -> None:
        self.tag = data.get("tag")
        self.name = data.get("name")
        self.icon: PlayerIcon = data.get("icon")
        self.trophies: int = data.get("trophies")
        self.role: MemberRole = data.get("role")
        self.nameColor: str = data.get("nameColor")
