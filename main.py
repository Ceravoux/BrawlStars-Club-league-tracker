import asyncio
import disnake
from disnake.ext.commands import InteractionBot
from commands import MyCog
from brawlstars import BrawlStarsClient
from loop import Loop, to_seconds_from_epoch
from database import (
    reset_club,
    insert_log,
    check_if_exists,
    inc_ticket_and_trophy,
    get_club_stats,
    get_club_info
)
from utils import format_member_stats, clubrank
from datetime import timezone, timedelta, datetime
from os import getenv
from dotenv import load_dotenv

load_dotenv()

loop = asyncio.new_event_loop()
client = BrawlStarsClient(api_key=getenv("API_KEY"))
loop.run_until_complete(client.start())

bot = InteractionBot(activity=disnake.Activity(name="B)"), loop=loop)
bot.add_cog(MyCog(client))


class ClubLeagueTracker:
    __slots__ = ("clubtag", "message", "channel_id")

    def __init__(self, clubtag: str, channel_id: int) -> None:
        self.clubtag = clubtag
        self.channel_id = channel_id
        self.message: disnake.Message = None

    async def set_message(self, msgid: int):
        channel = await bot.fetch_channel(self.channel_id)
        self.message = await channel.fetch_message(msgid)

    async def send_club_stats(self, stats):
        now = datetime.utcnow()
        desc, trophy = format_member_stats(stats)
        club_info = get_club_info(self.clubtag)
        embed = (
            disnake.Embed(
                title=f"{now.date()} | {stats[0]['clubname']}'s Club League",
                description=desc,
            )
            .add_field(
                name=f"Total Eligible Member: {len(stats)}",
                value="\u200b",
                inline=False,
            )
            .add_field(
                name=f"Total Trophy: {trophy}",
                value=f"last updated at <t:{to_seconds_from_epoch(now)}>",
                inline=False,
            )
            .set_thumbnail(
                clubrank[club_info["rank"]]
            )
        )
        channel = await bot.fetch_channel(self.channel)
        self.message = await channel.send(embed=embed)

    async def update_club_stats(self):
        stats = get_club_stats(self.clubtag)
        now = datetime.utcnow()

        if self.message is None:
            await self.reset_club_and_send_club_stats(client, self.clubtag)

        embed = self.message.embeds[0]
        embed.description, trophy = format_member_stats(stats)
        embed.set_field_at(
            1,
            name=f"Total Trophy: {trophy}",
            value=f"last updated at <t:{to_seconds_from_epoch(now)}>",
            inline=False,
        )
        self.message = await self.message.edit(embeds=[embed])

    async def watcher(self):
        members = await client.get_club_members(self.clubtag)
        for m in members:
            logs = await client.get_battle_log(m.tag)
            for l in logs:
                if l.battleTime.day != datetime.now(
                    tz=BS_TIMEZONE
                ).day or check_if_exists(m.tag, l.battleTime):
                    continue

                # HACK: do this better?
                if l.is_regular_CL_random() or l.is_regular_CL_team():
                    insert_log(m.tag, l, 1)
                    inc_ticket_and_trophy(m.tag, 1, l.trophyChange)

                if l.is_power_match_CL_random() or l.is_power_match_CL_team():
                    insert_log(m.tag, l, 2)
                    inc_ticket_and_trophy(m.tag, 2, l.trophyChange)

        await self.update_club_stats()

    async def reset_club_and_send_club_stats(self):
        data = await reset_club(client, self.clubtag)
        await self.send_club_stats(data[1])


tracker = ClubLeagueTracker("#28VJP0PUV", 930056474787446824)

# Brawl Stars Clan League begins and ends at UTC-9
BS_TIMEZONE = timezone(timedelta(hours=-9))

# TODO: integrate this into commands so anyone can set this
# on their own server. Input clubtags and channel id
# to receive updates then store them in database (maybe)
# Open multiple processes to run the updates with
# the multiprocessing module (maybe)
_club_member_update = Loop(
    loop=loop,
    coro=tracker.reset_club_and_send_club_stats,
    timezone=BS_TIMEZONE,
    weekday=(2,),
    pause=timedelta(days=7),
)
_club_league_monitor = Loop(
    loop=loop,
    coro=tracker.watcher,
    timezone=BS_TIMEZONE,
    weekday=(2, 4, 6),
    pause=timedelta(days=7),
    interval=600,
)

@bot.listen()
async def on_ready():
    await tracker.set_message(1065206079849504848)
    await asyncio.gather(_club_league_monitor.start(), _club_member_update.start())


@bot.listen()
async def on_disconnect():
    """To track bot's disconnection"""
    print("disconnected at", disnake.utils.utcnow())


bot.run(getenv("TOKEN"))