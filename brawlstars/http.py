from aiohttp import ClientSession
from urllib.parse import quote
from .models.battle import Battle
from .models.brawler import Brawler
from .models.player import Player
from .models.club import Club, ClubMember
from .models.events import ScheduledEvent
from .models.errors import (
    BadRequest,
    NotFound,
    Forbidden,
    TooManyRequests,
    BrawlStarsServerError,
)
from asyncio import sleep
from typing import AsyncGenerator

class BrawlStarsClient:
    __slots__ = ("api_key", "base", "session")
    def __init__(self, *, api_key: str = None) -> None:
        self.api_key = api_key
        self.base = "https://api.brawlstars.com/v1"
        self.session: ClientSession

    async def start(self):
        if self.api_key is None:
            raise RuntimeError("no api key")
        self.session = ClientSession(
            headers={"Authorization": "Bearer " + self.api_key}
        )

    async def _request(self, url) -> dict | None:
        if self.session is None:
            raise RuntimeError("session was not set; run client.start() first")
        async with self.session.get(url) as resp:
            data = await resp.json()
            match resp.status:
                case 200:
                    return data
                case 400:
                    raise BadRequest(resp.status, data)
                case 403:
                    raise Forbidden(resp.status, data)
                case 404:
                    raise NotFound(resp.status, data)
                case 429:
                    raise TooManyRequests(resp.status, data)
                case 500 | 503:
                    raise BrawlStarsServerError(resp.status, data)

    async def get_player(self, playerTag: str) -> Player:
        """Get information about a single player
        by player tag. Player tags can be found
        either in game or by from clan member list.

        Parameters
        ----------
        playerTag: `int`
            Tag of the player.

        """
        url = "{0}/players/{1}".format(self.base, quote(playerTag))
        data = await self._request(url)
        return Player(data)

    async def get_club(self, clubTag: str) -> Club:
        """Get information about a single clan by club tag.
        Club tags can be found in game.

        Parameters
        ----------
        clubTag: `str`
            Tag of the club.
        """
        url = "{0}/clubs/{1}".format(self.base, quote(clubTag))
        data = await self._request(url)
        return Club(data)

    async def get_club_members(self, clubTag: str, **kwargs) -> AsyncGenerator[ClubMember, None]:
        """List club members.

        Parameters
        ----------
        clubTag: `str`
            Tag of the club.
        before:
        after:
        limit: `int`
            Limit the number of items returned in the response.
        """

        url = "{0}/clubs/{1}/members".format(self.base, quote(clubTag))
        data = await self._request(url)
        async def clubmembers():
            for i in data["items"]:
                yield ClubMember(i)
                await sleep(0)
        return clubmembers()

    async def get_battle_log(self, playerTag: str, *, sort: int = 1) -> AsyncGenerator[Battle, None]:
        """Get list of recent battle results for a player.
        NOTE: It may take up to 30 minutes for a new battle
        to appear in the battlelog.

        Parameters
        ----------
        playerTag: `int`
            Tag of the player.
        sort: `int`
            -1 for ASCENDING (default) or 1 for DESCENDING
        """
        if sort not in (-1, 1):
            raise ValueError("sort is not -1 or 1")
        url = "{0}/players/{1}/battlelog".format(self.base, quote(playerTag))
        data = await self._request(url)
        async def battlelogs():
            for i in data["items"][::sort]:
                yield Battle(i)
                await sleep(0)
        return battlelogs()


    async def get_brawler(self, brawlerId: int):
        """Get information about a brawler.

        Parameters
        ----------
        brawlerId: `Enum[BrawlerOptions]`
            Identifier of the brawler.
        """
        url = "{0}/brawlers/{1}".format(self.base, quote(str(brawlerId)))
        data = await self._request(url)
        return Brawler(data)

    async def get_event_rotation(self, /):
        #XXX should return list
        """Get event rotation for ongoing events."""
        url = "{0}/events/rotation".format(self.base)
        data = await self._request(url)
        return ScheduledEvent(data)

    async def player_is_club_member(self, playertag: str, clubtag: str):
        try:
            player = await self.get_player(playertag)
        except Exception as e:
            raise e
        else:
            return player.club.tag == str(clubtag)
