from django import forms


class UserInputForm(forms.Form):
    user_strings = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': "Enter comma seperated Steam IDs",
                   'aria - describedby': "user_strings_help"
                   }
        )
    )
