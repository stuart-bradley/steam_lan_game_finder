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
        data = self.cleaned_data['user_strings']
        data = data.split(",")
        if len(data) < 2:
            print("ERROR")
            raise ValidationError(
                _('Could not split input into two or more Steam IDs'))
        return data
