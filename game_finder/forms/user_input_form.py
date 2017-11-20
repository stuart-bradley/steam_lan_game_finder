from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class UserInputForm(forms.Form):
    user_strings = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': "Enter comma seperated Steam IDs",
                   }
        )
    )

    def clean_user_strings(self):
        """ Overrides base method, checks data before processing. """
        data = self.cleaned_data['user_strings']
        # Removes empty strings and extra whitespace.
        data = list(map(str.strip, filter(None, data.split(","))))
        if len(data) < 2:
            raise ValidationError(
                _('Could not split input into two or more Steam IDs')
            )

        if len(data) > len(set(data)):
            raise ValidationError(
                _('Two or more inputs are identical')
            )
        return data
