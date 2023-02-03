from PIL import Image, ImageFilter
from re import compile
from brawlstars.models import Battle, BrawlerInfo

_subscript_table = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
_alphanumeric_regex = compile(r"[^a-z0-9]")


def to_gif(path, names):
    """in order to create emotes that the bot can use
    and make the most of server emote capacity
    we'll create animated emojis that changes ever
    so slightly"""

    for i in names:
        im1 = Image.open(path + "/{}.png".format(i))
        im2 = im1.copy().filter(ImageFilter.DETAIL)

        im1.save(
            path + "/{}.gif".format(i),
            append_images=[im2, im1],
            duration=100,
            save_all=True,
        )


def get_emoji(string: str):
    return _emoji.get(_alphanumeric_regex.sub("", string.lower()))


def subscript(s):
    return str(s).translate(_subscript_table)


def format_brawler_info(brawlerinfo: BrawlerInfo):
    return "{}{} [{:4d}] ".format(
        get_emoji(brawlerinfo.name),
        subscript(brawlerinfo.power).rjust(2, " "),
        brawlerinfo.trophies,
    )


def format_battle_log(battle: Battle):
    fmt = f"{battle.event.mode} | {battle.event.map}\n{battle.result} {battle.trophyChange:+2} 🏆\n"
    for t in battle.teams:
        for p in t:
            fmt += format_brawler_info(p.brawler) + p.name + "\n"
    for p in battle.players:
        fmt += format_brawler_info(p.brawler) + p.name + "\n"

    return fmt


def format_member_stats(stats: list[dict]) -> tuple[str, int]:
    string = ""
    trophy = 0
    for s in stats:
        string += "{:2d}/14🎟️ {:2d} 🏆 | {}\n".format(
            s["tickets"], s["trophy"], s["playername"]
        )
        trophy += s["trophy"]
    return string, trophy


_emoji = {
    "8bit": "<:8bit:1059019245612191776>",
    "amber": "<:amber:1059019248153939980>",
    "ash": "<:ash:1059019250196545538>",
    "barley": "<:barley:1059019252247572611>",
    "bea": "<:bea:1059019254265036910>",
    "belle": "<:belle:1059019256462839808>",
    "bibi": "<:bibi:1059019258396418048>",
    "bo": "<:bo:1059019260300632146>",
    "brock": "<:brock:1059019262305501285>",
    "bull": "<:bull:1059019264708853851>",
    "buzz": "<:buzz:1059019266516598875>",
    "byron": "<:byron:1059019268445970443>",
    "carl": "<:carl:1059019271457493103>",
    "colette": "<:colette:1059019273965686805>",
    "colt": "<:colt:1059019277883166750>",
    "darryl": "<:darryl:1059019281381199962>",
    "edgar": "<:edgar:1059019285445492826>",
    "emz": "<:emz:1059019289484595301>",
    "eve": "<:eve:1059019291237822515>",
    "frank": "<:frank:1059019295587315752>",
    "gene": "<:gene:1059019299395731526>",
    "grom": "<:grom:1059019303166414888>",
    "jacky": "<:jacky:1059019306119213157>",
    "leon": "<:leon:1059019310481289238>",
    "lola": "<:lola:1059019312649744406>",
    "max": "<:max:1059019316781142076>",
    "mortis": "<:mortis:1059019320677642300>",
    "mrp": "<:mrp:1059019323169050644>",
    "nita": "<:nita:1059019326922960896>",
    "penny": "<:penny:1059019330710421557>",
    "piper": "<:piper:1059019333608677456>",
    "rico": "<:rico:1059019337500983367>",
    "sandy": "<:sandy:1059019340915154975>",
    "shelly": "<:shelly:1059019343826010166>",
    "sprout": "<:sprout:1059019347496013915>",
    "stu": "<:stu:1059019351338008659>",
    "tara": "<:tara:1059019355473592382>",
    "tick": "<:tick:1059019358367649882>",
    "meg": "<:meg:1059023624377483304>",
    "lou": "<:lou:1059023626239737966>",
    "nani": "<:nani:1059023628907327588>",
    "pam": "<:pam:1059023630807355433>",
    "poco": "<:poco:1059023632606699592>",
    "rosa": "<:rosa:1059023635148443688>",
    "spike": "<:spike:1059023637304320010>",
    "surge": "<:surge:1059023639451803748>",
    "squeak": "<:squeak:1059023641960009728>",
    "gale": "<:gale:1059023794179674194>",
    "griff": "<:griff:1059023796180369418>",
    "jessie": "<:jessie:1059023798726303824>",
    "bonnie": "<a:bonnie:1059035850832347176>",
    "buster": "<a:buster:1059035854477209651>",
    "chester": "<a:chester:1059035858470174760>",
    "ruffs": "<a:ruffs:1059035860844163133>",
    "crow": "<a:crow:1059035863717249095>",
    "dynamike": "<a:dynamike:1059035866892337152>",
    "elprimo": "<a:elprimo:1059035869014655076>",
    "fang": "<a:fang:1059035871891959838>",
    "gray": "<a:gray:1059035875146731570>",
    "gus": "<a:gus:1059035876971261953>",
    "janet": "<a:janet:1059035880247005224>",
    "mandy": "<a:mandy:1059035883078156348>",
    "otis": "<a:otis:1059035885934485505>",
    "sam": "<a:sam:1059035889763889183>",
}
clubrank = {
    "bronze1": "https://media.discordapp.net/attachments/1058823341345095815/1065969265771024404/bronze1.png",
    "bronze2": "https://media.discordapp.net/attachments/1058823341345095815/1065969266186276965/bronze2.png",
    "bronze3": "https://media.discordapp.net/attachments/1058823341345095815/1065969266458890352/bronze3.png",
    "silver1": "https://media.discordapp.net/attachments/1058823341345095815/1065969334805069904/silver1.png",
    "silver2": "https://media.discordapp.net/attachments/1058823341345095815/1065969335018999878/silver2.png",
    "silver3": "https://media.discordapp.net/attachments/1058823341345095815/1065969335371300884/silver3.png",
    "gold1": "https://media.discordapp.net/attachments/1058823341345095815/1065969267478118400/gold1.png",
    "gold2": "https://media.discordapp.net/attachments/1058823341345095815/1065969267729780817/gold2.png",
    "gold3": "https://media.discordapp.net/attachments/1058823341345095815/1065969307785363568/gold3.png",
    "diamond1": "https://media.discordapp.net/attachments/1058823341345095815/1065969266710560818/diamond1.png",
    "diamond2": "https://media.discordapp.net/attachments/1058823341345095815/1065969266991583313/diamond2.png",
    "diamond3": "https://media.discordapp.net/attachments/1058823341345095815/1065969267226447913/diamond3.png",
    "mythic1": "https://media.discordapp.net/attachments/1058823341345095815/1065969309370814494/mythic1.png",
    "mythic2": "https://media.discordapp.net/attachments/1058823341345095815/1065969309765091358/mythic2.png",
    "mythic3": "https://media.discordapp.net/attachments/1058823341345095815/1065969310159343707/mythic3.png",
    "legend1": "https://media.discordapp.net/attachments/1058823341345095815/1065969308120924240/legend1.png",
    "legend2": "https://media.discordapp.net/attachments/1058823341345095815/1065969308464844841/legend2.png",
    "legend3": "https://media.discordapp.net/attachments/1058823341345095815/1065969308754247740/legend3.png",
    "masters": "https://media.discordapp.net/attachments/1058823341345095815/1065969309060448256/masters.png",
}