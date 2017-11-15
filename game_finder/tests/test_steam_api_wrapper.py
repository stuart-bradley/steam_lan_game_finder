from django.test import TestCase
from game_finder.steam_api_wrapper.steam_api_wrapper import *


class SteamAPIWrapperTestCase(TestCase):

    def test_convert_to_steam_ids(self):
        user_strings_valid = ['darkstarone93',
                              'https://steamcommunity.com/profiles/76561198006943469',
                              'https://steamcommunity.com/profiles/76561198142284524',
                              'smeagle100',
                              'https://steamcommunity.com/profiles/76561198038441365']
        user_strings_invalid = ["", "jgekkjgferkhjge", 101082]

        # Assert valid
        steam_ids = convert_to_steam_ids(user_strings_valid)
        for steam_id in steam_ids.values():
            self.assertTrue(steam_id.is_valid())

        # Assert invalid
        steam_ids = convert_to_steam_ids(user_strings_invalid)
        for steam_id in steam_ids.values():
            self.assertIsNone(steam_id)