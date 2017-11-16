from django.test import TestCase
from game_finder.steam_api_wrapper.steam_api_wrapper import *
from game_finder.models import Game


class SteamAPIWrapperTestCase(TestCase):
    def setUp(self):
        self.user_strings_valid = ['darkstarone93',
                                   'https://steamcommunity.com/profiles/76561198006943469',
                                   'https://steamcommunity.com/profiles/76561198142284524',
                                   'smeagle100',
                                   'https://steamcommunity.com/profiles/76561198038441365']

    def test_get_json_response(self):
        # Test urls relate to Dota2 (570).
        test_urls = [
            "http://store.steampowered.com/api/appdetails?appids=570&cc=us",
            "https://steamspy.com/api.php?request=appdetails&appid=570"
        ]
        for url in test_urls:
            self.assertIsNotNone(get_json_response(url),
                                 msg="{} returned None".format(url))

    def test_get_price(self):
        price = get_price('570')
        self.assertEqual(Decimal('0.0'), price)

    def test_find_new_game(self):
        appid = 570
        Game.objects.get(pk=appid).delete()
        game = find_new_game(str(appid))
        self.assertIsInstance(game, Game)

    def test_convert_to_steam_ids(self):
        user_strings_invalid = ["", "jgekkjgferkhjge", 101082]

        # Assert valid
        steam_ids = convert_to_steam_ids(self.user_strings_valid)
        for steam_id in steam_ids.values():
            self.assertTrue(steam_id.is_valid())

        # Assert invalid
        steam_ids = convert_to_steam_ids(user_strings_invalid)
        for steam_id in steam_ids.values():
            self.assertIsNone(steam_id)

    def test_create_user_games_list(self):
        user_string = "darkstarone93"
        persona_string = "Lutras Debtra_76561198011864860"
        steam_ids = convert_to_steam_ids([user_string])
        games_list = create_user_games_list(steam_ids)
        self.assertIsInstance(next(iter(games_list[persona_string].values())),
                              Game)

    def test_create_combinations(self):
        user_games = OrderedDict()
        user_games["player_1"] = {'1': 'game_1', '2': 'game_2'}
        user_games["player_2"] = {'1': 'game_1', '3': 'game_3'}
        user_games["player_3"] = {'1': 'game_1', '4': 'game_4'}
        result = create_combinations(user_games)
        test_key = ("player_1", "player_2", "player_3")
        self.assertTrue(test_key in result.keys())
        self.assertEqual(result[test_key], {'1': 'game_1'})

    def test_steam_api_wrapper(self):
        result = create_combinations_from_user_input(self.user_strings_valid)
        self.assertIsInstance(result, OrderedDict)
