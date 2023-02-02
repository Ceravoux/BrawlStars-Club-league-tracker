import asyncio
import disnake
from disnake.ext.commands import InteractionBot
from commands import MyCog
from brawlstars import BrawlStarsClient
from brawlstars.enums import ClubRank
from loop import Loop, from_weekday
from database import (
    reset_club,
    insert_log,
    check_if_exists,
    inc_ticket_and_trophy,
    get_club_stats,
    get_clubs,
    create_battle_id,
    insert_club,
    insert_discord_info,
    edit_discord_info,
    remove_server_logs,
    get_server_logs,
    export_battle_logs,

)
from utils import format_member_stats, clubrank
from datetime import timezone, timedelta, datetime
import streamlit as st


loop = asyncio.new_event_loop()
client = BrawlStarsClient(api_key=st.secrets["API_KEY"])
loop.run_until_complete(client.start())

bot = InteractionBot(activity=disnake.Activity(name="clubs", type=disnake.ActivityType.watching), loop=loop)
bot.add_cog(MyCog(client))


async def send_club_stats(stats, clubinfo):
    now = datetime.utcnow()
    desc, trophy = format_member_stats(stats)

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
            value=f"last updated at <t:{now.timestamp():.0f}>",
            inline=False,
        )
        .set_thumbnail(clubrank[clubinfo["clubrank"]])
    )
    for i in clubinfo["discord"]:
        try:
            channel = await bot.fetch_channel(i["channelid"])
        except:
            edit_discord_info(
                {"channelid":0}, clubinfo["clubtag"], i["serverid"]
            )
            continue
        message = await channel.send(embed=embed)
        edit_discord_info({"messageid": message.id}, clubinfo["clubtag"], i["serverid"])


async def update_club_stats(clubinfo):
    stats = get_club_stats(clubinfo["clubtag"])
    messages:list[disnake.Message] = []

    for i in clubinfo["discord"]:
        try:
            channel = await bot.fetch_channel(i["channelid"])
        except:
            edit_discord_info(
                {"channelid":0}, clubinfo["clubtag"], i["serverid"]
            )
            continue
        try:
            message = await channel.fetch_message(i["messageid"])
        except:
            loop.create_task(send_club_stats(stats, clubinfo))
            continue
        else:
            messages.append(message)

    if messages == []:
        return
    now = datetime.utcnow()
    embed = messages[0].embeds[0]
    embed.description, trophy = format_member_stats(stats)
    embed.set_field_at(
        1,
        name=f"Total Trophy: {trophy}",
        value=f"last updated at <t:{now.timestamp():.0f}>",
        inline=False,
    )

    if now.astimezone(BS_TIMEZONE) > CL_WEEK:
        export_battle_logs(CL_WEEK, clubinfo["clubtag"])
        await asyncio.gather(*(m.edit(embeds=[embed], file="club_league_logs.json") for m in messages))

    await asyncio.gather(*(m.edit(embeds=[embed]) for m in messages))
    


# HACK: do this better?
async def CL_watcher():
    today = datetime.now(tz=BS_TIMEZONE).day 
    for c in get_clubs():
        members = await client.get_club_members(c["clubtag"])
        async for m in members:
            logs = await client.get_battle_log(m.tag)
            async for l in logs:
                if l.battleTime.day != today or check_if_exists(
                    create_battle_id(m.tag, l.battleTime), "club_league", "battle_id"
                ):
                    continue

                if l.is_regular_CL_random() or l.is_regular_CL_team():
                    insert_log(m.tag, l, 1)
                    inc_ticket_and_trophy(m.tag, 1, l.trophyChange)

                elif l.is_power_match_CL_random() or l.is_power_match_CL_team():
                    insert_log(m.tag, l, 2)
                    inc_ticket_and_trophy(m.tag, 2, l.trophyChange)

        await update_club_stats(c)


async def reset_club_and_send_club_stats(clubinfo):
    data = await reset_club(client, clubinfo["clubtag"])
    await send_club_stats(data[1], clubinfo)


async def CL_setter():
    data = get_clubs()
    for i in data:
        await reset_club_and_send_club_stats(i)
    update_CL_WEEK()
    

@bot.listen()
async def on_ready():
    await asyncio.gather(_club_league_monitor.start(), _club_member_update.start())


@bot.listen()
async def on_disconnect():
    """To track bot's disconnection"""
    print("disconnected at", disnake.utils.utcnow())


@bot.slash_command()
async def set_cl_log(inter: disnake.AppCmdInter, clubtag: str, rank: ClubRank, channelid = None):
    """set club league log of given clubtag on this server
    Parameters
    ----------
    clubtag: 
    channelid: `int`
        Where the log will be set.
        Defaults to current channel.
    """
    # wait a while
    await inter.response.defer(with_message=True)
    try:
        await client.get_club(clubtag)
    except Exception as e:
        return await inter.followup.send(*e.args)

    # check database
    if not check_if_exists(clubtag, "clubs", "clubtag"):
        insert_club(clubtag, ClubRank(rank).name)

    if check_if_exists(inter.guild_id, "discord", "serverid"):
        return await inter.followup.send(f"Logs for {clubtag} has been set in this server!")
    insert_discord_info(clubtag, inter.guild_id, channelid or inter.channel_id)
    await inter.followup.send(f"Successfully set a log for {clubtag}.")


@bot.slash_command()
async def remove_cl_log(inter:disnake.AppCmdInter):
    "remove particular clan league log on this server"
    view = disnake.ui.View(timeout=90)
    await inter.response.defer(with_message=True)
    await inter.followup.send(view=view.add_item(LogSelect(inter.guild_id)))


class LogSelect(disnake.ui.StringSelect):
    def __init__(self, serverid):
        logs = get_server_logs(serverid)
        super().__init__(
            custom_id="log", 
            placeholder="Select a log(s) to be removed.", 
            max_values=len(logs),
            options=[disnake.SelectOption(label=i["clubtag"]) for i in logs]
        )
    async def callback(self, inter:disnake.AppCmdInter):
        await inter.response.defer(with_message=True)
        remove_server_logs(inter.guild_id, self.values)
        await inter.followup.send(f"Successfully removed log(s) for {self.values}")
 

# Brawl Stars Clan League begins and ends at UTC-9
# but we give some leniency for first and last updates
# because some people do club league at last minutes
BS_TIMEZONE = timezone(timedelta(hours=-9, minutes=-5))

_club_member_update = Loop(
    loop=loop,
    coro=CL_setter,
    timezone=BS_TIMEZONE,
    weekday=(2,),
    pause=timedelta(days=7),
)
_club_league_monitor = Loop(
    loop=loop,
    coro=CL_watcher,
    timezone=BS_TIMEZONE,
    weekday=(2, 4, 6),
    pause=timedelta(days=7),
    interval=600,
)

def update_CL_WEEK():
    global CL_WEEK
    CL_WEEK = CL_WEEK + timedelta(days=7)

CL_WEEK = from_weekday(0, tzinfo=BS_TIMEZONE) - timedelta(days=7, minutes=5)

async def keep_alive():
    await asyncio.sleep(60)
    print("time:", disnake.utils.utcnow())
    loop.create_task(keep_alive())

loop.create_task(keep_alive())
loop.run_until_complete(bot.start(st.secrets["TOKEN"]))
