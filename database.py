from os import getenv
from dotenv import load_dotenv
from supabase import create_client
from loop import to_seconds_from_epoch
from brawlstars.http import BrawlStarsClient

load_dotenv()

supabase = create_client(getenv("SUPABASE_URL"), getenv("SUPABASE_KEY"))
club_members_table = supabase.table("club_members")
club_league_table = supabase.table("club_league")
clubs_table = supabase.table("clubs")

def create_battle_id(playertag, battletime):
    return f"{playertag[1:]}{to_seconds_from_epoch(battletime)}"


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
        for p in clubmembers
    ]
    oldmembers = club_members_table.delete().eq("clubtag", club.tag).execute()
    newmembers = club_members_table.insert(clubmembers).execute()
    return oldmembers.data, newmembers.data


def insert_log(playertag: str, log, tickets: int):
    # NOTE: does not support showdowns
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
            "time": to_seconds_from_epoch(log.battleTime),
        }
    ).execute()
    return data.data


def check_if_exists(playertag, battletime):
    id = create_battle_id(playertag, battletime)
    data = club_league_table.select("battle_id").eq("battle_id", id).execute()
    if not data.data:
        return False
    return True


def inc_ticket_and_trophy(ptag: str, tix: int, trophychange: int):
    data = supabase.rpc(
        "inc_ticket_and_trophy",
        {"ptag": ptag, "tix": tix, "trophychange": trophychange},
    ).execute()
    return data.data


def get_club_stats(clubtag):
    data = club_members_table.select("*").eq("clubtag", clubtag).execute()
    return data.data


def get_member_log(membertag):
    data = supabase.rpc(
        "get_member_log",
        {"membertag": membertag}
    ).execute()
    return data.data


def insert_club_info(clubtag, clubrank, serverid, channelid):
    data = clubs_table.insert(
        {
            "clubtag": clubtag,
            "clubrank": clubrank,
            "serverid": serverid,
            "channelid": channelid,
            "messageid": 0,
        }
    ).execute()
    return data.data


def get_club_info(clubtag):
    data = clubs_table.select("clubtag").eq("clubtag", clubtag).execute()
    return data.data

