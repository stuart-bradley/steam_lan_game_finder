from django.shortcuts import render
from game_finder.forms.user_input_form import UserInputForm
import game_finder.steam_api_wrapper.steam_api_wrapper as steam_api


def index(request):
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


def index_helper(results, form):
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
