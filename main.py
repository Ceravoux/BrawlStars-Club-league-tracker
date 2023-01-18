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
)
from utils import format_member_stats
from datetime import timezone, timedelta, datetime
from os import getenv
from dotenv import load_dotenv

load_dotenv()

loop = asyncio.new_event_loop()
client = BrawlStarsClient(api_key=getenv("API_KEY"))
loop.run_until_complete(client.start())

bot = InteractionBot(activity=disnake.Activity(name="B)"), loop=loop)
bot.add_cog(MyCog(client))

CLUBTAG = "#28VJP0PUV"

MESSAGE: disnake.Message = None


async def send_club_stats(stats, channel_id=1058823341345095815):
    global MESSAGE
    now = datetime.utcnow()
    embed = (
        disnake.Embed(
            title=f"{now.date()} | {stats[0]['clubname']}'s Club League",
            description="\n".join(format_member_stats(i) for i in stats),
        )
        .add_field(
            name="\u200b\n",
            value=f"last updated at <t:{to_seconds_from_epoch(now)}>",
            inline=False,
        )
        .set_thumbnail(
            "https://media.discordapp.net/attachments/1058823341345095815/1060589200749113464/clubleague.png"
        )
    )
    channel = await bot.fetch_channel(channel_id)
    MESSAGE = await channel.send(embed=embed)


async def update_club_stats():
    global MESSAGE
    stats = get_club_stats(CLUBTAG)
    now = datetime.utcnow()
    embed = MESSAGE.embeds[0]
    embed.description = "\n".join(format_member_stats(i) for i in stats)
    embed.set_field_at(
        0,
        name="\u200b\n",
        value=f"last updated at <t:{to_seconds_from_epoch(now)}>",
        inline=False,
    )
    MESSAGE = await MESSAGE.edit(embeds=[embed])


async def watcher(clubtag):
    members = await client.get_club_members(clubtag)
    for m in members:
        logs = await client.get_battle_log(m.tag)
        for l in logs:
            if l.battleTime.day != datetime.now(BS_TIMEZONE=BS_TIMEZONE).day \
                or check_if_exists(m.tag, l.battleTime):
                continue

            # HACK: do this better?
            if l.is_regular_CL_random() or l.is_regular_CL_team():
                insert_log(m.tag, l, 1)
                inc_ticket_and_trophy(m.tag, 1, l.trophyChange)

            if l.is_power_match_CL_random() or l.is_power_match_CL_team():
                insert_log(m.tag, l, 2)
                inc_ticket_and_trophy(m.tag, 2, l.trophyChange)

    await update_club_stats()


async def reset_club_and_send_club_stats(client, clubtag):
    data = await reset_club(client, clubtag)
    await send_club_stats(data[1])


# Brawl Stars Clan League begins and ends at UTC-9
BS_TIMEZONE = timezone(timedelta(hours=-9))

# TODO: integrate this into commands so anyone can set this
# on their own server. Input clubtags and channel id
# to receive updates then store them in database (maybe)
# Open multiple processes to run the updates with
# the multiprocessing module (maybe)
_club_member_update = Loop(
    loop=loop,
    coro=reset_club_and_send_club_stats,
    timezone=BS_TIMEZONE,
    weekday=(2,),
    pause=timedelta(days=7),
)
_club_league_monitor = Loop(
    loop=loop,
    coro=watcher,
    timezone=BS_TIMEZONE,
    weekday=(2, 4, 6),
    pause=timedelta(days=7),
    interval=600,
)


@bot.listen()
async def on_ready():
    await asyncio.gather(
        _club_member_update.start(client, CLUBTAG), _club_league_monitor.start(CLUBTAG)
    )


@bot.listen()
async def on_disconnect():
    """To track bot's disconnection"""
    print("disconnected at", disnake.utils.utcnow())


bot.run(getenv("TOKEN"))
