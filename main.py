import asyncio
import disnake
from disnake.ext.commands import InteractionBot
from commands import MyCog
from brawlstars import BrawlStarsClient
from loop import Loop, from_weekday
from database import (
    reset_club,
    insert_log,
    check_if_exists,
    inc_ticket_and_trophy,
    get_club_members,
    get_clubs,
    create_battle_id,
    edit_discord_info,
    export_battle_logs,
)
from utils import format_member_stats, clubrank
from datetime import timezone, timedelta, datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Initialise the event loop so the bot
# will not create its own
loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)

client = BrawlStarsClient(email=os.getenv("EMAIL"), password=os.getenv("PWD"))


bot = InteractionBot(
    activity=disnake.Activity(name="your club", type=disnake.ActivityType.watching),
    loop=loop,
)
bot.add_cog(MyCog(client))


@bot.listen()
async def on_disconnect():
    """To track bot's disconnection"""
    print(f"disconnected at {datetime.now(timezone(timedelta(hours=7)))}")


@bot.listen()
async def on_ready():
    print(f"on_ready : {datetime.now(timezone(timedelta(hours=7)))}")


async def send_club_stats(
    members: list[dict], discord_info, club_name, club_tag, club_rank
):
    now = datetime.utcnow()
    desc, trophy = format_member_stats(members)

    embed = (
        disnake.Embed(
            title=f"{now.date()} | {club_name}'s Club League",
            description=desc,
        )
        .add_field(
            name=f"Total Eligible Member: {len(members)}",
            value="\u200b",
            inline=False,
        )
        .add_field(
            name=f"Total Trophy: {trophy}",
            value=f"last updated at <t:{now.timestamp():.0f}:f> <t:{now.timestamp():.0f}:R>",
            inline=False,
        )
        .set_thumbnail(clubrank[club_rank])
    )

    try:
        channel = await bot.fetch_channel(discord_info["channelid"])
    except:
        edit_discord_info({"channelid": 0}, club_tag, discord_info["serverid"])
        return
    message = await channel.send(embed=embed)
    edit_discord_info({"messageid": message.id}, club_tag, discord_info["serverid"])


async def update_club_stats(data):
    members = get_club_members(data["clubtag"])
    messages: list[disnake.Message] = []
    for i in data["discord"]:
        try:
            channel = await bot.fetch_channel(i["channelid"])
        except:
            edit_discord_info({"channelid": 0}, data["clubtag"], i["serverid"])
            continue
        try:
            message = await channel.fetch_message(i["messageid"])
        except:
            loop.create_task(
                send_club_stats(
                    members,
                    i,
                    members[0]["clubname"],
                    data["clubtag"],
                    data["clubrank"],
                )
            )
            continue
        else:
            messages.append(message)

    if messages == []:
        return
    now = datetime.utcnow()
    embed = messages[0].embeds[0]
    embed.description, trophy = format_member_stats(members)
    embed.set_field_at(
        1,
        name=f"Total Trophy: {trophy}",
        value=f"last updated at <t:{now.timestamp():.0f}>",
        inline=False,
    )

    if now.astimezone(BS_TIMEZONE) > CL_WEEK:
        export_battle_logs(CL_WEEK, data["clubtag"])
        await asyncio.gather(
            *(
                m.edit(embed=embed, file=disnake.File("club_league_logs.json"))
                for m in messages
            )
        )
        await reset_club(client, data["clubtag"])
        return

    await asyncio.gather(*(m.edit(embed=embed) for m in messages))


async def check_logs(member, logs):
    today = datetime.now(tz=BS_TIMEZONE).day
    async for l in logs:
        if l.battleTime.day != today or check_if_exists(
            create_battle_id(member.tag, l.battleTime), "club_league", "battle_id"
        ):
            continue

        if l.is_regular_CL_random() or l.is_regular_CL_team():
            insert_log(member.tag, l, 1)
            inc_ticket_and_trophy(member.tag, 1, l.trophyChange)

        elif l.is_power_match_CL_random() or l.is_power_match_CL_team():
            insert_log(member.tag, l, 2)
            inc_ticket_and_trophy(member.tag, 2, l.trophyChange)


# HACK: do this better?
async def CL_watcher():
    data = get_clubs()
    for d in data:
        members = await client.get_club_members(d["clubtag"])

        async for m in members:
            logs = await client.get_battle_log(m.tag)
            loop.create_task(check_logs(m, logs))
        await update_club_stats(d)


# Brawl Stars Club League begins and ends at 00:00 UTC-9
# but we give some leniency for first and last updates
# because some people do club league at last minutes
BS_TIMEZONE = timezone(timedelta(hours=-9, minutes=-5))
CL_WEEK = from_weekday(0, tzinfo=timezone(timedelta(hours=-9)))


_club_league_monitor = Loop(
    loop=loop,
    coro=CL_watcher,
    timezone=BS_TIMEZONE,
    weekday=(2, 4, 6),
    pause=timedelta(days=7),
    interval=600,
)


async def starter():
    await bot.wait_until_first_connect()
    await asyncio.gather(_club_league_monitor.start())


loop.run_until_complete(asyncio.gather(bot.start(os.getenv("TOKEN")), starter()))
