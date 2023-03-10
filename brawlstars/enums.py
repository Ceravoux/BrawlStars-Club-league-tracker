from enum import Enum, auto


class ClubType(str, Enum):
    open = auto()
    closed = auto()
    inviteOnly = auto()
    unknown = auto()


class MemberRole(str, Enum):
    notMember = auto()
    member = auto()
    president = auto()
    senior = auto()
    vicePresident = auto()
    unknown = auto()


class EventMode(str, Enum):
    soloShowdown = auto()
    duoShowdown = auto()
    heist = auto()
    bounty = auto()
    siege = auto()
    gemGrab = auto()
    brawlBall = auto()
    bigGame = auto()
    bossFight = auto()
    roboRumble = auto()
    takedown = auto()
    loneStar = auto()
    presentPlunder = auto()
    hotZone = auto()
    superCityRampage = auto()
    knockout = auto()
    volleyBrawl = auto()
    basketBrawl = auto()
    holdTheTrophy = auto()
    trophyThieves = auto()
    duels = auto()
    wipeout = auto()
    data = auto()
    botDrop = auto()
    hunters = auto()
    lastStand = auto()
    snowtelThieves = auto()
    unknown = auto()


class BrawlerOptions(Enum):
    """# NOTE: this is incomplete!!"""
    SHELLY = 16000000
    BROCK = 16000003
    RICO = 16000004
    SPIKE = 16000005
    NITA = 16000008
    DYNAMIKE = 16000009
    CROW = 16000012
    POCO = 16000013
    PIPER = 16000015
    PAM = 16000016
    TARA = 16000017
    FRANK = 16000020
    GENE = 16000021
    SANDY = 16000028
    BEA = 160000029
    EMZ = 16000030
    MAX = 16000032
    JACKY = 16000034
    GALE = 1600000035
    SURGE = 16000038
    STU = 16000045
    BELLE = 16000046
    GRIFF = 16000050
    BONNIE = 16000058
    OTIS = 16000059
    SAM = 16000060
    GUS = 16000061
    BUSTER = 16000062
    CHESTER = 16000063
    MANDY = 16000064


class ClubRank(Enum):
    BRONZE1 = 11
    BRONZE2 = 12
    BRONZE3 = 13
    SILVER1 = 21
    SILVER2 = 22
    SILVER3 = 23
    GOLD1 = 31
    GOLD2 = 32
    GOLD3 = 33
    DIAMOND1 = 41
    DIAMOND2 = 42
    DIAMOND3 = 43
    MYTHIC1 = 51
    MYTHIC2 = 52
    MYTHIC3 = 53
    LEGEND1 = 61
    LEGEND2 = 62
    LEGEND3 = 63
    MASTERS = 70
