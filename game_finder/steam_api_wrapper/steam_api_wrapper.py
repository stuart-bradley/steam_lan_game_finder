from collections import OrderedDict
from steam import SteamID
from steam import WebAPI
import environ
import requests
from decimal import Decimal
from time import sleep
from game_finder.models import Game, Tag
import itertools
from operator import itemgetter

"""
This is the Steam API Wrapper module. It's purpose is to parse user input into
a series of Steam IDs, from which lists of Games are generated, which are then
intersected to find multiplayer games in common.

Method order is generally as follows (the result from each method feeding into
the next):
1. convert_to_steam_ids
2. create_user_games_list
3. create_combinations

All other methods feed into the above three, the whole system can be run via:
create_combinations_from_user_input
"""


def create_combinations_from_user_input(user_strings):
    """ Runs whole module in one go. """
    steam_ids = convert_to_steam_ids(user_strings)
    users = create_user_games_list(steam_ids)
    ordered_games_list = create_combinations(users)
    return ordered_games_list

""" Methods for handling Steam IDs. """

def convert_to_steam_ids(user_strings):
    """ Wrapper for converting multiple steam ids.

        Keyword arguments:
        user_strings -- list of user inputs.

        Returns a dict with correct steam_ids or None as values.
    """
    steam_ids = OrderedDict()
    for user_string in user_strings:
        if isinstance(user_string, str):
            steam_id = convert_to_steam_id(user_string)
            persona_name = get_persona_name(steam_id)
            if persona_name:
                steam_ids[persona_name] = steam_id
            else:
                steam_ids[user_string] = steam_id
        else:
            steam_ids[user_string] = None
    return steam_ids


def convert_to_steam_id(user_string):
    """ Generates valid steam IDs from user input.

        Keyword arguments:
        user_string -- input from user
    """

    # Converts URL format to standard format.
    user_string = user_string.split("/")[-1]
    steam_id = SteamID(user_string)
    if steam_id.is_valid():
        return steam_id
    else:  # Failure can be due to vanity usernames.
        steam_id = convert_from_vanity_url_to_steam_id(user_string)
        if steam_id:
            return steam_id
        else:
            return None


def get_persona_name(steam_id):
    """ Attempts to get persona name of steam user. """
    if isinstance(steam_id, SteamID):
        env = environ.Env()
        web_api = WebAPI(env('STEAM_API_KEY'))

        content = web_api.ISteamUser.GetPlayerSummaries(
            steamids=steam_id.as_64)
        try:
            persona_name = content["response"]["players"][0]["personaname"]
            return "_".join([persona_name, str(steam_id.as_64)])
        except Exception as e:
            print(e)
            return None
    else:
        return None

def convert_from_vanity_url_to_steam_id(user_string):
    """ Tries to create a SteamID object via the URL. """
    if user_string.isdigit():
        return SteamID.from_url(
            "http://steamcommunity.com/profiles/{}".format(user_string))
    else:
        return SteamID.from_url(
            "http://steamcommunity.com/id/{}".format(user_string))

""" Methods for generating games lists. """

def create_user_games_list(steam_ids):
    """ Grabs list of multiplayer steam games for each valid user. """

    env = environ.Env()
    web_api = WebAPI(env('STEAM_API_KEY'))

    users = OrderedDict()
    for user_string, steam_id in steam_ids.items():
        games = web_api.IPlayerService.GetOwnedGames(
            steamid=steam_id.as_64,
            include_played_free_games=True, appids_filter=[],
            include_appinfo=True)
        if not games['response']:
            users[user_string] = None
        else:
            users[user_string] = {}
            for game in games['response']['games']:
                appid = int(game['appid'])
                try:
                    db_entry = Game.objects.get(pk=appid)
                except Game.DoesNotExist as e:
                    db_entry = find_new_game(str(appid))
                    if db_entry is None:
                        continue
                if db_entry.is_multiplayer:
                    users[user_string][str(game['appid'])] = db_entry

    return users


def create_combinations(users):
    """ Creates intersection dicts of shared games. """


    if len(users) < 2:
        return None

    ordered_games_lists = OrderedDict()

    # Generate tuples of combinations of users of all lengths.
    combinations_of_users = []
    for i in range(2, len(users) + 1):
        combinations_of_users.extend(
            itertools.combinations(list(users.keys()), i))

    # Perform intersection.
    for combin in combinations_of_users:
        if len(combin) == 2:
            intersect = users[combin[0]].keys() & users[
                combin[-1]].keys()
            ordered_games_lists[combin] = {k: v for k, v in
                                           users[combin[0]].items() if
                                           k in intersect}
        else:   # If previous intersections have been generated,
                # the previous ones can be used to decrease computing
                # time of later ones.
            intersect = ordered_games_lists[combin[0:len(combin) - 1]] & \
                        users[combin[-1]].keys()
            ordered_games_lists[combin] = {k: v for k, v in
                                           ordered_games_lists[combin[0:len(
                                               combin) - 1]].items() if
                                           k in intersect}

    ordered_games_lists = sort_ordered_games_list(ordered_games_lists)

    return ordered_games_lists

""" Helper methods. """

def get_json_response(url):
    """ Returns a JSON response and handles errors. """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Skipping {}".format(url))
        print(e)
        return None


def get_price(appid):
    """ Attempts to get price data for a game from the Steam Store. """
    sleep(1)  # Sleep to stop failed API requests.
    price_content = get_json_response(
        "http://store.steampowered.com/api/appdetails?appids={}&cc=us".format(
            appid))
    try:
        if price_content:
            if price_content[str(appid)]["data"]["is_free"]:
                return Decimal('0.00')
            price_string = str(
                price_content[str(appid)]["data"]["price_overview"]["initial"])
            # String must have it's decimal added.
            return Decimal(price_string[:-2] + "." + price_string[-2:])
        else:
            return Decimal('-1.0')
    except KeyError as e:
        return Decimal('-1.0')

def find_new_game(appid):
    """ Attempts to find and add a game to the DB """
    multiplayer_tags = set(Tag.objects.filter(is_multiplayer=True).values_list(
        'name', flat=True))
    all_tags = set(Tag.objects.values_list('name', flat=True))

    game_data = get_json_response(
            "https://steamspy.com/api.php?request=appdetails&appid={}".format(
                appid))
    if game_data:
        game_tags = []
        game_multiplayer_tags = []
        if game_data['tags']:
            game_tags = game_data['tags'].keys()
            game_multiplayer_tags = game_tags & multiplayer_tags
            missing_tags = game_tags - all_tags
            # Creates tags as needed.
            for item in missing_tags:
                if item in multiplayer_tags:
                    tag = Tag(name=item, is_multiplayer=True)
                else:
                    tag = Tag(name=item)
                tag.save()
        # Creates Games.
        game_name = game_data["name"]
        if game_name:
            if len(game_multiplayer_tags) > 0:
                price = get_price(appid)
                game = Game(appid=int(appid), title=game_name, price=price,
                            is_multiplayer=True)
                game.save()
            else:
                game = Game(appid=int(appid), title=game_name)
                game.save()
            for key in game_tags:
                try:
                    tag = Tag.objects.get(name=key)
                    game.tags.add(tag)
                except Tag.DoesNotExist as e:
                    continue
            game.save()
            return game
    return None


def sort_ordered_games_list(ordered_games_lists):
    """ Reverses as sorts ordered games lists alphabetically """

    print(ordered_games_lists)

    new_order = OrderedDict()

    for group, games in reversed(ordered_games_lists.items()):
        new_order[group] = OrderedDict(
            sorted(games.items(), key=lambda x: x[1].title))

    return new_order
