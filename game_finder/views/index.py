from django.shortcuts import render

from game_finder.forms.user_input_form import UserInputForm


def index(request):
    results = None

    if request.method == 'POST':
        form = UserInputForm(request.POST)
        if form.is_valid():
            results = form.cleaned_data['user_strings']
    else:
        form = UserInputForm()

    return render(request, 'games/index.html', {
        'form': form,
        'results': results,
    })
