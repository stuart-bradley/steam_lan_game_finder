# Steam Game List Intersector

The Steam Game List Intersector is a web app that uses the Steam API to find multiplayer games that users have in common.
The idea is that due to the burgeoning size of Steam libraries (mine is 500+ games), it can be hard to quickly work out
which games everyone has in common. 

Additionally, because of how the intersections work, the app also displays the games owned by subsets of the users 
inputted along with the price so that the user(s) not in the subset know how much it would cost to buy without jumping 
into steam.

## Screenshot

![Index_View](index_view2.png)

## Usage

In the form field, a user can enter a comma delimited list of Steam IDs in any format (the website displays examples of 
the formats). Once this is done and submitted, a large amount of processing is done (takes a few seconds for five users).

Once the processing is successful, a carousel appears with a table showing the multiplayer games shared across **all** users. 
Moving the carousel brings up different tables showing shared games across different user subsets.

All tables also display pricing information, which can be updated via AJAX if the user thinks it might be out-of-date. 

## Installation Notes

The app itself is fairly simple, and runs on a small number of technologies:
* [Python](https://www.python.org/) (v3.6.3) - Backend.
    * [Django](https://www.djangoproject.com/) (v1.11).
    * [steam](https://pypi.python.org/pypi/steam) (v0.8.22) - (Python package that does the Steam API calls).
    * [requests](http://docs.python-requests.org/en/master/) (v2.18.4) - (Python package that handles non-Steam API calls).
    * [Django-environ](https://github.com/joke2k/django-environ) (v0.4.4) - (Python package for storing ENV variables).
* [Yarn](https://yarnpkg.com/en/) (v1.3.2) - Package management.
    * [Jquery](https://jquery.com/) (v3.2.1).
* [Webpack](https://webpack.js.org/) (v3.8.1) - Package management.
* [Bootstrap](https://getbootstrap.com/) (v4.0.0-beta.2) - Frontend.
    * [Bootswatch - Slate](https://bootswatch.com/slate/) (v4.0) - (Modified with custom css).
* [Font Awesome](http://fontawesome.io/) (v4.7.0) - Frontend (due to Webpack issues Font Awesome is loaded via CDN).

The original plan was to include React for the front end, but the additional complexity didn't seem necessary. This is 
why Yarn and Webpack are used to load Bootstrap (which could have easily also been done via CDN). Both Yarn and Webpack 
could be removed for a simpler Python application. 

### `.env` 

This file should be stored in the `steam_lan_game_finder` folder:

```
DEBUG=on
SECRET_KEY= 
# Should be in dj-database-url format: https://github.com/kennethreitz/dj-database-url
DATABASE_URL=mysql://user:password@localhost:3306/schema_name
# Get an API key from https://steamcommunity.com/dev/apikey
STEAM_API_KEY= 
```
 
### Migration Notes

The second migration file ([`migrations/0002_seed_games_and_tags.py`](https://github.com/lutrasdebtra/steam_lan_game_finder/blob/master/game_finder/migrations/0002_seed_games_and_tags.py))
populates the database through a large number of API calls. A single call gets a list of all Steam Games from 
[steamspy.com](https://steamspy.com/about), after which the Steam Store API is called approximately sixteen thousand 
times (with one second between calls to avoid DDoS protection) to get initial pricing information. 

This can take a few hours, so when testing it is **heavily** recommended that the `--keepdb` tag be used.
  
Alternatively, the file could be modified to just set all prices to `Decimal('-1.0')`, which displays as `??`, and users 
can AJAX update the database over time. This will not impact the test suite in any way. 

### Yarn Build Scripts

Since Webpack build commands can be a bit verbose, the following yarn scripts can be run using `yarn run XXX`:

```
 "build": "webpack --config webpack.base.config.js --progress --colors",
 "build-production": "webpack --config webpack.prod.config.js --progress --colors",
 "watch": "webpack --config webpack.base.config.js --watch --progress --colors"
```

## Running As A Standalone Script

[`SteamLanGameFinder.py`](https://github.com/lutrasdebtra/steam_lan_game_finder/blob/master/standalone/SteamLanGameFinder.py)
is the original script which does not require the full web interface. To use it by itself the requirements are:
* [Python](https://www.python.org/) (v3.*).
    * [steam](https://pypi.python.org/pypi/steam) (v0.8.22).
    * [requests](http://docs.python-requests.org/en/master/) (v2.18.4).
    
To use the file, line 19 must be updated with the API key, which can be procured from [here](https://steamcommunity.com/dev/apikey).
Once that is done the class can be initialised with a list of Steam IDs, which will return an `OrderedDict` of intersects
in the same format as the main web application uses. Keep in mind these are not formatted nicely, and may require some
post-processing. 
 