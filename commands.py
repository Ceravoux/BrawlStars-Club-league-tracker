import disnake
from disnake.ext import commands
from inspect import cleandoc
from brawlstars import BrawlStarsClient
from utils import format_battle_log
from brawlstars.enums import BrawlerOptions
from database import get_member_log
from loop import to_datetime_from_seconds
import re

def slash_command(docstring="", **kwargs):
    """cuts description to 100chars for slash commands."""
    docstring = cleandoc(docstring)
    def decorator(func):
        if func.__doc__ is not None:
            return commands.slash_command()(func)

        m = re.search(r"Parameters", docstring)
        if m:
            desc =  docstring[:m.start()]
            if len(desc) > 100:
                desc = desc[:100]
            func.__doc__ = desc + "\n" + docstring[m.start():]
        else:
            func.__doc__ = docstring
        return commands.slash_command(**kwargs)(func)
    return decorator


class MyCog(commands.Cog):
    def __init__(self, client: BrawlStarsClient) -> None:
        super().__init__()
        self.client = client

    @slash_command()
    async def help(inter: disnake.AppCmdInter):
        "Shows some information about the commands."
        await inter.response.send_message(
            "A bot for monitoring club league. "
            "Aside from that most features are incomprehensive (im lazy), "
            "and thus may fail to meet your standards. "
            "Feel free to contribute at https://github.com/Ceravoux/BrawlStars-Club-league-tracker. "
            "For any issues or complaints, please file an issue or pm Vallery#0627. "
        )

    @slash_command(BrawlStarsClient.get_player.__doc__)
    async def get_player_info(
        self, inter: disnake.AppCmdInter, playertag: commands.String[5, 12]
    ):
        await inter.response.defer()
        try:
            player = await self.client.get_player(playertag)
        except Exception as e:
            await inter.followup.send(*e.args)
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

        await inter.followup.send(
            "Maybe someday I'll make the brawler part...", embed=emb
        )

    @slash_command(BrawlStarsClient.get_brawler.__doc__)
    async def get_brawler_info(self, inter: disnake.AppCmdInter, brawler):
        await inter.response.defer(with_message=True)
        try:
            b = await self.client.get_brawler(BrawlerOptions[brawler].value)
        except Exception as e:
            await inter.followup.send(*e.args)
            raise e

        emb = disnake.Embed(
            title=b.name,
            description=f"Gadgets: {b.gadgets}\n StarPowers: {b.starPowers}",
        )
        emb.set_thumbnail(
            file=disnake.File(f"/app/brawlstars-club-league-tracker/brawlstars/assets/brawlers/{b.name.lower()}.png")
        )
        await inter.followup.send(
            content="I hope I will make this better... someday...", embed=emb
        )

    @get_brawler_info.autocomplete("brawler")
    async def autocomplete(inter, input: str):
        return [i.name for i in BrawlerOptions if input.upper() in i.name][:25]

    @slash_command(BrawlStarsClient.get_battle_log.__doc__)
    async def get_battle_log(
        self, inter: disnake.AppCmdInter, playertag: commands.String[5, 12]
    ):
        await inter.response.defer()
        try:
            log = await self.client.get_battle_log(playertag, sort=1)
            log = [i async for i in log]
        except Exception as e:
            await inter.followup.send(*e.args)
            raise e

        l = len(log)
        emb = [disnake.Embed(title="Battle log")] * (1 + l // 10)
        for n in range(l):
            emb[n // 10].add_field(
                name=f"{log[n].battle.type} - {log[n].battleTime}",
                value=format_battle_log(log[n]),
            )

        await inter.followup.send(embeds=emb)

    @slash_command()
    async def get_member_cl_log(
        self, inter: disnake.AppCmdInter, membertag: commands.String[5, 12]
    ):
        """gets the club league log of a member 
        during the last(current) club league week."""
        await inter.response.defer()
        try:
            logs = get_member_log(membertag)
        except Exception as e:
            await inter.followup.send(*e.args)
            raise e

        embed = disnake.Embed(
            title="{}'s Club League Log".format(logs[0]["playername"])
        )
        for i in logs:
            embed.add_field(
                name=to_datetime_from_seconds(i["time"]),
                value=f'{i["map"]} | {i["result"]} {i["trophychange"]:+2} 🏆\n'
                f'{i["team"]} vs {i["opponent"]}',
                inline=False,
            )
        await inter.followup.send(embed=embed)
