'''
display_name : 2nde
team_id      : m19xws6dqtrkjby4asiqgb9gth
invite_id    : hsys7jg41bgotqagneakpmda4e


Team n° 1
name         : qkzk
display_name : qkzk
team_id      : 1nse3b6fd3bypx1dycry3x4pfe
invite_id    : joimwq3ntiyxim9mtdgwwjrqrr


Team n° 2
name         : nsi-terminale
display_name : NSI Terminale
team_id      : zussekp53bnbfpw4azhnz59oda
invite_id    : c3n1hsik938s5rxet7zoyii3aw


Team n° 3
name         : nsi-premiere
display_name : NSI premiere
team_id      : nwrndt3pjbfzf8iawrab4mzdpa
invite_id    : b19euyaepbnptnj95mt8z8oicw

get_list_of_channels_by_ids(self, team_id, options=None)


ici il faut recréer un script à part
qui associe tous les canaux à une channel_id

si possible dans chaque team

ensuite construire un log utilisable

ensuite intégrer le bash script à python pour update auto

ensuite créer un service qui enregistre les logs auto

ensuite les afficher qq part et trier par user

ensuite créer un script qui récupere tous les noms d'user

proposer au bot d'afficher SI l'user qui demande est admin de la team

'''
from datetime import datetime
from pprint import pprint
from robert_le_robot import robert_le_robot, get_options, create_driver

PATH_TABLE_CHANNEL = './table_channel.txt'
TEAMS = {

    "m19xws6dqtrkjby4asiqgb9gth": "seconde",
    "1nse3b6fd3bypx1dycry3x4pfe": "qkzk",
    "zussekp53bnbfpw4azhnz59oda": "nsi-terminale",
    "nwrndt3pjbfzf8iawrab4mzdpa": "nsi-premiere",
}


def get_channels_by_team(team_id):
    driver = create_driver()
    driver.login()
    return driver.teams.get_public_channels(team_id)


def get_channel_list():
    channel_dict = {}
    for team_id in TEAMS:
        channels_for_team = []
        for channel_info in get_channels_by_team(team_id):
            cleaned_channel = clean_channel_data(channel_info)
            channels_for_team.append(cleaned_channel)
        channel_dict[TEAMS[team_id]] = channels_for_team
    return channel_dict


def get_channel_list():
    channel_dict = {}
    for team_id in TEAMS:
        for channel_info in get_channels_by_team(team_id):
            cleaned_channel = clean_channel_data(channel_info)
            channel_dict[cleaned_channel['id']] = cleaned_channel

    return channel_dict


def clean_channel_data(channel_info):
    cleaned_channel = {
        "display_name": channel_info['display_name'],
        "name": channel_info['name'],
        "team_id": channel_info['team_id'],
        "id": channel_info['id'],
        "team_name": TEAMS[channel_info['team_id']]
    }
    return cleaned_channel


def read_file():
    with open(PATH_TABLE_CHANNEL) as f:
        lines = [line.rstrip() for line in f]
    return lines


def parse_lines(lines):
    data_list = []
    for line in lines:
        elems = line.split('|')
        if len(elems) > 2:
            data_list.append(cast_line(elems))
    return data_list


def cast_line(elems):
    data_dict = {"channel_id": elems[0].strip()}

    jointime = elems[1].strip()
    try:
        jointime = datetime.fromtimestamp(int(jointime) / 1000)
    except (ValueError, TypeError) as e:
        jointime = None

    leavetime = elems[2].strip()
    try:
        leavetime = datetime.fromtimestamp(int(leavetime) / 1000)
    except (ValueError, TypeError) as e:
        leavetime = None

    data_dict["jointime"] = jointime
    data_dict["leavetime"] = leavetime

    return data_dict


def add_channel_description(data_list, channel_dict):

    for reference in data_list:
        channel_id = reference['channel_id']

        channel = channel_dict.get(reference['channel_id'])
        if channel is not None:
            reference['channel_name'] = channel['name']
            reference['display_name'] = channel['display_name']
            reference['team'] = channel.get('team_name')
    return data_list


def drive():
    channel_dict = get_channel_list()

    lines = read_file()
    connection_list = parse_lines(lines)
    connection_list = add_channel_description(connection_list, channel_dict)
    connection_list.sort(key=lambda x: x["jointime"], reverse=True)

    pprint(connection_list)


if __name__ == '__main__':

    drive()
