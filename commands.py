import disnake
from disnake.ext import commands
from brawlstars import BrawlStarsClient
from utils import format_battle_log
from brawlstars.enums import BrawlerOptions, ClubRank
from database import get_member_log, insert_club_info
from loop import to_datetime_from_seconds
import re

def slash_command(docstring):
    def decorator(func):
        m = re.search(r"Parameters", docstring)
        if m:
            desc =  re.sub(r"\n        ", " ", docstring[:m.start()])
            if len(desc) > 100:
                desc = desc[:100]
                print(desc)
            func.__doc__ = desc + "\n" + docstring[m.start():]
            print(len(func.__doc__))
            print(func.__doc__)
        else:
            func.__doc__ = docstring


        return commands.slash_command()(func)
    return decorator


class MyCog(commands.Cog):
    def __init__(self, client: BrawlStarsClient) -> None:
        super().__init__()
        self.client = client

    @slash_command("Shows some information about the commands.")
    async def help(inter: disnake.AppCmdInter):
        
        await inter.response.send_message(
            "For monitoring club league. "
            "Aside from that most features are incomplete (im lazy), "
            "and thus may fail to meet your standards. "
            "Feel free to contribute at https://github.com/Ceravoux"
        )

    @slash_command(BrawlStarsClient.get_player.__doc__)
    # @commands.slash_command()
    async def get_player_info(
        self, inter: disnake.AppCmdInter, playertag: commands.String[5, 12]
    ):
    
        try:
            player = await self.client.get_player(playertag)
        except Exception as e:
            await inter.response.send_message(*e.args)
            raise e

        emb = disnake.Embed(
            title="Player Info",
            description="\n".join(
                "{}: {}".format(k, getattr(player, k))
                for k in (
                    "name",
                    "tag",
                    "trophies",
                    "highestTrophies",
                    "soloVictories",
                    "duoVictories",
                    "_3vs3Victories",
                    "club",
                )
            ),
        )

        await inter.response.send_message(
            content="Maybe someday I'll make the brawler part...", embed=emb
        )

    # @slash_command(BrawlStarsClient.get_brawler.__doc__)
    @commands.slash_command()
    async def get_brawler_info(self, inter: disnake.AppCmdInter, brawler):
        """
        Creates a weekly task.

        Parameters
        ----------
        timezone: only supports UTC; e.g. -09:00 for UTC-09:00 (defaults to UTC+00)
        weekday: Mon/Tue/Wed/Thu/Fri/Sat/Sun
        time: e.g. 08:42:15
        details: e.g. Feed dog homework
        """
        try:
            b = await self.client.get_brawler(BrawlerOptions[brawler].value)
        except Exception as e:
            await inter.response.send_message(*e.args)
            raise e

        emb = disnake.Embed(
            title=b.name,
            description=f"Gadgets: {b.gadgets}\n StarPowers: {b.starPowers}",
        )
        emb.set_thumbnail(
            file=disnake.File(r"brawlstars\assets\brawlers\{}.png".format(b.name))
        )
        await inter.response.send_message(
            content="I hope I will make this better... someday...", embed=emb
        )

    @get_brawler_info.autocomplete("brawler")
    async def autocomplete(inter, input: str):
        return [i.name for i in BrawlerOptions if input.upper() in i.name][:25]

    # @slash_command(BrawlStarsClient.get_battle_log.__doc__)
    @commands.slash_command()
    async def get_battle_log(
        self, inter: disnake.AppCmdInter, playertag: commands.String[5, 12]
    ):
        try:
            log = await self.client.get_battle_log(playertag, sort=1)
        except Exception as e:
            return await inter.response.send_message(*e.args)

        l = len(log)
        emb = [disnake.Embed(title="Battle log")] * (1 + l // 10)
        for n in range(l):
            emb[l // 10].add_field(
                name=f"{log[n].battle.type} - {log[n].battleTime}",
                value=format_battle_log(log[n]),
            )

        await inter.response.send_message(embeds=[emb])

    @slash_command("Gets the clan league battle log of a player.")
    async def get_member_cl_log(
        self, inter: disnake.AppCmdInter, membertag: commands.String[5, 12]
    ):
        try:
            logs = get_member_log(membertag)
        except Exception as e:
            await inter.response.send_message(*e.args)
            raise e

        embed = disnake.Embed(
            title="{}'s Club League Log".format(logs[0]["playername"])
        )
        for i in logs:
            embed.add_field(
                name=to_datetime_from_seconds(i["time"]),
                value=f'{i["map"]} | {i["result"]} {i["trophychange"]:+2} 🏆\n'
                      f'{i["team"]} vs {i["opponent"]}',
                inline=False
            )
        await inter.response.send_message(embed=embed)

    @slash_command("Sets a clan league log for a club.")
    async def set_cl_log(self, inter:disnake.AppCmdInter, clubtag:str, rank: ClubRank):
        insert_club_info(clubtag, ClubRank(rank).name, inter.guild_id, inter.channel_id)
        await inter.response.send_message("Success.")