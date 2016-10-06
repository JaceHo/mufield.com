from django import forms


class MusicForm(forms.Form):
    title = forms.CharField(label=u"Title", max_length=128, required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    player = forms.CharField(label=u"Singer", max_length=128, required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    url = forms.CharField(label=u"URL", max_length=1024, required=False,
                          widget=forms.TextInput(attrs={'class': 'form-control'}))

