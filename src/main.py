#!python3

import sys
import os
import requests

def print_help():
    message = """
    RuneScore fetches a RuneScape player's stats from Jagex' servers,
    and then creates a formatted HTML table out of the data.

    Command-line arguments:
      --player-name [PLAYER NAME]
        * When used, the script will use the included name.
        * Example: $ src/main.py --player-name "Diapolo 10"

      --osrs
        * Use Old School RuneScape hiscores instead of RS3 ones
        * Alternative flag: --oldschool
        * Example: $ src/main.py --osrs --player-name Ironman-Dia

      --help
        * Display this tooltip and close the program
        * Alternative flag: -h
        * Example: $ src/main.py --help

    @2017 copyright Lari Liuhamo
    """
    print(message)

def argparse(args):
    player_name = None

    hiscores = ""
    # Values: "" for RS3, "_oldschool" for OSRS

    gamemode = ""
    # Values: "" for normal player,
    #         "_ironman" for ironman,
    #         "_ultimate" for UIM,
    #         "_hardcore" for HCIM

    # Let's store whether the last flag required a value
    value = False

    try:
        for index, arg in enumerate(args):

            if arg == "--player-name":
                player_name = args[index + 1]
                value = True

            elif arg in ("--osrs", "--oldschool"):
                hiscores = "_oldschool"

            elif arg == "--ironman":
                gamemode = "_ironman"

            elif arg in ["--uim", "--ultimate", "--ultimate-ironman"]:
                gamemode = "_ultimate"

            elif arg in ["--hcim", "--hardcore", "--hardcore-ironman"]:
                gamemode = "_hardcore"

            elif arg in ("-h", "--help"): #TODO: Implement help function
                print_help()
                sys.exit()

            else:
                if not value:
                    raise TypeError
                value = False

    except IndexError:
        sys.exit(f"Error: '{arg}' requires a value, which was not provided")

    except TypeError:
        sys.exit(f"Error: '{arg}' is not a valid argument or flag")

    # Because RS3 doesn't have UIM mode:
    if hiscores != "_oldschool" and gamemode == "_ultimate":
        sys.exit("Error: RS3 does not have Ultimate Ironman mode")

    return (player_name, hiscores, gamemode)


def get_stats(player_name, hiscores="", gamemode=""):

    page = requests.get(
        f'http://services.runescape.com/m=hiscore{hiscores}{gamemode}/index_lite.ws?player={player_name}'
    )

    return [
        stat for stat in [

            # Turn each skill's XP, level and rank into lists
            skill.split(",") for skill in page.text.split("\n")
            ]

        # Since we don't want to get minigame hiscores, we scrap them
        if len(stat)==3
        ]

def format_html(player_stats, hiscores="", gamemode=""):

    # Since we cannot get skill names from Jagex' servers, we have to provide the data ourselves.
    SKILL_NAMES = ("Total", "Attack", "Defence",
                   "Strength", "Constitution", "Ranged",
                   "Prayer", "Magic", "Cooking",
                   "Woodcutting", "Fletching", "Fishing",
                   "Firemaking", "Crafting", "Smithing",
                   "Mining", "Herblore", "Agility",
                   "Thieving", "Slayer", "Farming",
                   "Runecrafting", "Hunter", "Construction",
                   "Summoning", "Dungeoneering",
                   "Divination", "Invention")

    html_output = ""
    row_template = "\n\t\t<td>{}</td>" * 4
    prefix = {"_ultimate": "UIM",
              "_hardcore": "HCIM",
              "_ironman":  "ironman",
              "":          "normal"
              }

    # Player stats are in the order Rank, Level, XP

    html_output += "<table class='hiscores'>"
    html_output += f"\n\t<!-- Using {prefix[gamemode]} ranking -->"
    html_output += f"\n\t<caption>My hiscores in {'OSRS' if hiscores == '_oldschool' else 'RS3'}</caption>"

    html_output += "\n\t<tr>"
    html_output += "\n\t\t<th>Skill</th>\n\t\t<th>Level</th>\n\t\t<th>XP</th>\n\t\t<th>Rank</th>"
    html_output += "\n\t</tr>"

    for index, skill in enumerate(player_stats):
        html_output += "\n\t<tr>"
        html_output += row_template.format(SKILL_NAMES[index], skill[1], skill[2], skill[0])
        html_output += "\n\t</tr>"

    html_output += "\n</table>"

    return html_output



def main():

    args = sys.argv[1:]
    player_name, hiscores, gamemode = argparse(args)

    if player_name is None:
        player_name = input("Username: ")

    # Spaces aren't valid in URLs
    player_name = player_name.replace(" ", "_").replace("-", "_")

    stats = get_stats(player_name, hiscores, gamemode)
    html = format_html(stats, hiscores, gamemode)

    with open(os.path.join(os.path.dirname(__file__), "hiscores", f"{player_name.lower()}.html"), "w") as f:
        f.write(html)

    sys.exit()

if __name__ == "__main__":
    main()
