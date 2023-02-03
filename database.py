from supabase import create_client
from brawlstars.http import BrawlStarsClient, Battle
import json
import streamlit as st


supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
club_members_table = supabase.table("club_members")
club_league_table = supabase.table("club_league")
clubs_table = supabase.table("clubs")
discord_table = supabase.table("discord")


def create_battle_id(playertag, battletime):
    return f"{playertag[1:]}{battletime.timestamp():.0f}"


async def reset_club(client: BrawlStarsClient, clubtag: str):
    club = await client.get_club(clubtag)
    clubmembers = await client.get_club_members(clubtag)
    clubmembers = [
        {
            "playertag": p.tag,
            "playername": p.name,
            "clubname": club.name,
            "clubtag": club.tag,
            "tickets": 0,
            "trophy": 0,
        }
        async for p in clubmembers
    ]
    oldmembers = club_members_table.delete().eq("clubtag", club.tag).execute()
    newmembers = club_members_table.insert(clubmembers).execute()
    return oldmembers.data, newmembers.data


def insert_log(playertag: str, log: Battle, tickets: int):
    """
    # NOTE: does not support showdowns
    # because club league is all 3v3
    """
    if playertag in (i.tag for i in log.teams[0]):
        team = [i.name for i in log.teams[0]]
        opponent = [i.name for i in log.teams[1]]
    else:
        team = [i.name for i in log.teams[1]]
        opponent = [i.name for i in log.teams[0]]

    data = club_league_table.insert(
        {
            "battle_id": create_battle_id(playertag, log.battleTime),
            "playertag": playertag,
            "team": team,
            "opponent": opponent,
            "map": log.event.map,
            "type": log.type,
            "result": log.result,
            "ticket": tickets,
            "trophychange": log.trophyChange,
            "time": round(log.battleTime.timestamp()),
        }
    ).execute()
    return data.data


def check_if_exists(arg, table, field):
    match table:
        case "club_league":
            _table = club_league_table
        case "club_members":
            _table = club_members_table
        case "clubs":
            _table = clubs_table
        case "discord":
            _table = discord_table
        case _:
            raise ValueError(f"the table '{table}' does not exist.")

    data = _table.select(field).eq(field, arg).execute()
    if not data.data:
        return False
    return True


def inc_ticket_and_trophy(ptag: str, tix: int, trophychange: int):
    data = supabase.rpc("inc_ticket_and_trophy", {"ptag": ptag, "tix": tix, "trophychange": trophychange}).execute()
    return data.data


def get_club_stats(clubtag):
    data = club_members_table.select("*").eq("clubtag", clubtag).execute()
    return data.data


def get_member_log(membertag):
    data = supabase.rpc("get_member_log", {"membertag": membertag}).execute()
    return data.data


def insert_club(clubtag, clubrank):
    data = (
        clubs_table.insert(
            {
                "clubtag": clubtag,
                "clubrank": clubrank.lower(),
            }
        )
        .execute()
    )
    return data.data

def insert_discord_info(
    clubtag: str, serverid: int, channelid: int
):
    data = discord_table.insert(
            {
                "clubtag": clubtag,
                "serverid": serverid,
                "channelid": channelid,
            }
        ).execute()
    
    return data.data


def get_clubs():
    """
    returns an `array` of {
        clubtag: str,
        clubrank: str,
        discord: [
            {serverid: int, channelid: int, messageid: int},
            {serverid: int, channelid: int, messageid: int},
            ...
        ]
    }
    """

    clubs = clubs_table.select("*").execute().data
    data = (
        discord_table.select("*")
        .neq("channelid", 0)
        .in_("clubtag", [i["clubtag"] for i in clubs])
        .execute()
        .data
    )
    for c in clubs:
        c["discord"] = [
            {
                "serverid": i["serverid"],
                "channelid": i["channelid"],
                "messageid": i["messageid"],
            }
            for i in data
            if i["clubtag"] == c["clubtag"]
        ]

    return clubs


def edit_discord_info(edit:dict, clubtag:str, serverid:int):
    data = (
        discord_table.update(edit)
        .eq("clubtag", clubtag)
        .eq("serverid", serverid)
        .execute()
    )
    return data.data


def get_server_logs(serverid):
    data = discord_table.select("*").eq("serverid", serverid).execute()
    return data.data


def remove_server_logs(serverid, clubtags: list):
    data = (
        discord_table.delete()
        .eq("serverid", serverid)
        .in_("clubtag", clubtags)
        .execute()
    )
    return data.data


def export_battle_logs(time, clubtag):
    logs = {"clubtag": clubtag, "ClubLeagueTime": str(time.date())}
    members = (
        club_members_table.select("playertag", "playername")
        .eq("clubtag", clubtag)
        .execute()
    )
    for d in members.data:
        data = club_league_table.select("*").eq("playertag", d["playertag"]).execute()
        logs[d["playername"]] = data.data
    with open("club_league_logs.json", "w", encoding="utf8") as f:
        json.dump(logs, f, ensure_ascii=False)
    print(f"exported club league logs for {clubtag} on {time}")
