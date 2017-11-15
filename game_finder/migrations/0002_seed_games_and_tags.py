# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-14 23:36
from __future__ import unicode_literals

from django.db import migrations
from game_finder.steam_api_wrapper.steam_api_wrapper import (get_json_response,
get_price)


class Migration(migrations.Migration):

    def forward(apps, schema_editor):
        """ Generates Game and Tag entities from the SteamSpy
        and SteamStore APIs.
        """
        print()

        Game = apps.get_model("game_finder", "Game")
        Tag = apps.get_model("game_finder", "Tag")
        multiplayer_tags = {'Multiplayer', 'Local Multiplayer',
                            'Co-Op', 'Co-op',
                            'Online Co-Op', 'Local Co-Op',
                            'Massively Multiplayer'}
        all_tags = {}

        print("Generating Games and Tags.")
        content = get_json_response("https://steamspy.com/api.php?request=all")

        if content:
            items_len = len(content.keys())
            counter = 0
            for appid, game_data in content.items():
                counter += 1
                game_tags = []
                game_multiplayer_tags = []
                if game_data['tags']:
                    game_tags = game_data['tags'].keys()
                    game_multiplayer_tags = game_tags & multiplayer_tags
                    missing_tags = game_tags - all_tags.keys()
                    # Creates tags as needed.
                    for item in missing_tags:
                        print("Creating Tag: {}".format(item))
                        if item in multiplayer_tags:
                            tag = Tag(name=item, is_multiplayer=True)
                        else:
                            tag = Tag(name=item)
                        tag.save()
                        all_tags[item] = tag
                # Creates Games.
                game_name = game_data["name"]
                print("Creating Game: {} ({}/{})".format(game_name, counter, items_len))
                if len(game_multiplayer_tags) > 0:
                    price = get_price(appid)
                    game = Game(appid=int(appid),title=game_name,price=price, is_multiplayer=True)
                    game.save()
                else:
                    game = Game(appid=int(appid), title=game_name)
                    game.save()
                for key in game_tags:
                    game.tags.add(all_tags[key])
                game.save()


    def backward(apps, schema_editor):
        """ Deletes all Game and Tag entries. """
        Game = apps.get_model("game_finder", "Game")
        Tag = apps.get_model("game_finder", "Tag")

        for tag in Tag.objects.all():
            tag.delete()

        for game in Game.objects.all():
            game.delete()

    dependencies = [
        ('game_finder', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward, backward)
    ]
