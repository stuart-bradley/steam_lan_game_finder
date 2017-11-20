from django.shortcuts import render
from game_finder.forms.user_input_form import UserInputForm
import game_finder.steam_api_wrapper.steam_api_wrapper as steam_api
from decimal import Decimal
from game_finder.models import Game
from django.http import JsonResponse
from game_finder.templatetags.game_extras import generate_price
from django.template.defaultfilters import date


def index(request):
    """ Main view, handles form processing. """
    results = None

    if request.method == 'POST':
        form = UserInputForm(request.POST)
        if form.is_valid():
            results = form.cleaned_data['user_strings']
            results, form = index_helper(results, form)
    else:
        form = UserInputForm()

    return render(request, 'games/index.html', {
        'form': form,
        'results': results,
    })


def update_price(request):
    """ AJAX request for getting proce data. """
    if request.is_ajax():
        appid = request.GET.get('appid', None)
        new_price = steam_api.get_price(appid)
        if new_price is not Decimal('-1.0'):
            try:
                db_entry = Game.objects.get(pk=int(appid))
                db_entry.price = new_price
                db_entry.save()
                modified_date = db_entry.modified_date

                data = {
                    'price': generate_price(new_price),
                    'modified_date': date(modified_date, 'Y-m-d')
                }

                return JsonResponse(data)
            except Game.DoesNotExist as e:
                return JsonResponse({
                    'error': 'Could not find appid {}'.format(appid)
                })

def index_helper(results, form):
    """ Index request helper which interacts with the Steam API Wrapper
        to do the various stages of processing and produce errors if
        needed.
    """
    steam_ids = steam_api.convert_to_steam_ids(results)
    for key, value in steam_ids.items():
        if value is None:
            form.add_error(None,
                           "Could not convert '{}' to a Steam ID".format(key))
            return None, form

    users = steam_api.create_user_games_list(steam_ids)

    for key, value in users.items():
        if value is None:
            form.add_error(None,
                           "Could not find {}'s games library. " +
                           "They might have a private account".format(key))
            return None, form

    ordered_games_list = steam_api.create_combinations(users)
    return ordered_games_list, form
