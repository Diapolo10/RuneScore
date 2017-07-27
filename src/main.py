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
    use_osrs_hiscores = False

    # Let's store whether the last flag required a value
    value = False

    try:
        for index, arg in enumerate(args):

            if arg == "--player-name":
                player_name = args[index + 1]
                value = True

            elif arg in ("--osrs", "--oldschool"):
                use_osrs_hiscores = True

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

    return (player_name, use_osrs_hiscores)


def get_stats(player_name, osrs=False):

    page = requests.get(
        f'http://services.runescape.com/m=hiscore{"_oldschool" if osrs else ""}/index_lite.ws?player={player_name}'
    )

    return [
        stat for stat in [

            # Turn each skill's XP, level and rank into lists
            skill.split(",") for skill in page.text.split("\n")
            ]

        # Since we don't want to get minigame hiscores, we scrap them
        if len(stat)==3
        ]

def format_html(player_stats, osrs=False):

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

    # Player stats are in the order Rank, Level, XP

    html_output += "<table class='hiscores'>"
    html_output += f"\n\t<caption>My hiscores in {'OSRS' if osrs else 'RS3'}</caption>"

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
    player_name, osrs = argparse(args)

    if player_name is None:
        player_name = input("Username: ")

    # Spaces aren't valid in URLs
    if " " in player_name:
        player_name = "_".join(player_name.split())

    stats = get_stats(player_name, osrs)
    html = format_html(stats, osrs)
    print(os.path.join(os.getcwd(), "hiscores", f"{player_name}.html"))
    with open(os.path.join(os.getcwd(), "hiscores", f"{player_name}.html"), "w") as f:
        f.write(html)
    sys.exit()

if __name__ == "__main__":
    main()
