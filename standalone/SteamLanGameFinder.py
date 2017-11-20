from collections import OrderedDict
from steam import SteamID
from steam import WebAPI
import itertools
import requests

"""
SteamLanGameFinder
Finds games that multiple users share in their Steam Libraries.
Stuart Bradley
2017-11-06

Requires the steam, and requests Python packages. 
"""


class SteamLanGameFinder:
    """ Finds overlapping games between groups of Steam Users. """
    api_key = ''

    def __init__(self, user_strings, database):
        self.database = database

        self.steam_IDs = self.convert_to_steam_IDs(user_strings)
        print(self.steam_IDs)
        self.web_api = WebAPI(SteamLanGameFinder.api_key)
        self.users = self.create_user_games_list()
        self.combinations = self.create_combinations()
        self.filter_multiplayer()

    def convert_to_steam_IDs(self, user_strings):
        """ Generates valid steam IDs from user input.

        Keyword arguements:
        user_strings -- input from user, a list of strings, e.g. ['user1', 'user2']
        """
        print("Converting Steam IDs")
        steam_IDs = OrderedDict()

        for user_string in user_strings:
            user_string = user_string.split("/")[
                -1]  # Converts URL format to standard format.
            steam_id = SteamID(user_string)
            if steam_id.is_valid():
                steam_IDs[user_string] = steam_id
            else:  # Failure can be due to vanity usernames.
                steam_id = self.convert_from_vanity_url_to_SteamID(
                    user_string)
                if steam_id is not None:
                    steam_IDs[user_string] = steam_id
                else:
                    raise SteamUserNotFoundError(user_string)
        return steam_IDs

    def convert_from_vanity_url_to_SteamID(self, user_string):
        """ Tries to create a SteamID object via the URL. """
        if user_string.isdigit():
            return SteamID.from_url(
                "http://steamcommunity.com/profiles/{}".format(user_string))
        else:
            return SteamID.from_url(
                "http://steamcommunity.com/id/{}".format(user_string))

    def create_user_games_list(self):
        """ Grabs list of steam games for each valid user. """
        print("Creating games lists")
        users = OrderedDict()
        for user_string, steam_id in self.steam_IDs.items():
            games = self.web_api.IPlayerService.GetOwnedGames(
                steamid=steam_id.as_64,
                include_played_free_games=True, appids_filter=[],
                include_appinfo=True)
            if not games['response']:
                raise SteamUserIsNotPublic(user_string)
            else:
                users[user_string] = {}
                for game in games['response']['games']:
                    users[user_string][str(game['appid'])] = game['name']
        return users

    def create_combinations(self):
        """ Creates intersection dicts of shared games. """

        print("Intersecting lists")
        if len(self.users) < 2:
            raise NotEnoughSteamIDsError()

        ordered_games_lists = OrderedDict()

        # Generate tuples of combinations of users of all lengths. 
        combinations_of_users = []
        print(list(self.users.keys()))
        for i in range(2, len(self.users) + 1):
            combinations_of_users.extend(
                itertools.combinations(list(self.users.keys()), i))

        if len(combinations_of_users) < 2:
            raise NotEnoughSteamIDsError()

        # Perform intersection.
        for combin in combinations_of_users:
            if len(combin) == 2:
                intersect = self.users[combin[0]].keys() & self.users[
                    combin[-1]].keys()
                ordered_games_lists[combin] = {k: v for k, v in
                                               self.users[combin[0]].items()
                                               if k in intersect}
            else:  # If previous intersections have been generated, the previous ones can be used to decrease computing time of later ones.
                intersect = ordered_games_lists[combin[0:len(combin) - 1]] & \
                            self.users[combin[-1]].keys()
                ordered_games_lists[combin] = {k: v for k, v in
                                               ordered_games_lists[combin[
                                                                   0:len(
                                                                       combin) - 1]].items()
                                               if k in intersect}

        return ordered_games_lists

    def filter_multiplayer(self):
        """ Filters shared games list by whether they are multiplayer """
        print("filter_multiplayer")
        ordered_games_lists_filtered = OrderedDict()
        for tup, games in self.combinations.items():
            ordered_games_lists_filtered[tup] = {}
            for k, v in games.items():
                if k in self.database.database and self.database.database[k]:
                    ordered_games_lists_filtered[tup][k] = v
        print(ordered_games_lists_filtered)


class PsuedoDatabase:
    def __init__(self):
        self.database = {}
        self.generate_database()

    def generate_database(self):
        response = requests.get("https://steamspy.com/api.php?request=all")
        multiplayer_tags = set(
            ['Multiplayer', 'Local Multiplayer', 'Co-Op', 'Co-op',
             'Online Co-Op', 'Local Co-Op', 'Massively Multiplayer'])
        content = response.json()
        for appid, game in content.items():
            if game['tags']:
                tags = game['tags'].keys()
                if len(multiplayer_tags & tags) > 0:
                    self.database[appid] = True
                else:
                    self.database[appid] = False


"""
Exception Classes
"""


class SteamUserNotFoundError(Exception):
    def __init___(self, user_string):
        Exception.__init__(self, "Inputted string was invalid: {}".format(
            user_string))


class SteamUserIsNotPublic(Exception):
    def __init___(self, user_string):
        Exception.__init__(self,
                           "Steam user {} is not publically accessible.".format(
                               user_string))


class NotEnoughSteamIDsError(Exception):
    def __init___(self, user_string):
        Exception.__init__(self, "At least two Steam IDs are required.")


if __name__ == "__main__":
    database = PsuedoDatabase()
    test = SteamLanGameFinder(['darkstarone93',
                               'https://steamcommunity.com/profiles/76561198006943469',
                               'https://steamcommunity.com/profiles/76561198142284524',
                               'smeagle100',
                               'https://steamcommunity.com/profiles/76561198038441365'],
                              database)
    # 76561198038441365, smeagle100, 76561198142284524, 76561198006943469, darkstarone93
