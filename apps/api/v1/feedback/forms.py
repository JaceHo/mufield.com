from django import forms

from apps.api.models import Feed


class FeedbackForm(forms.ModelForm):
    """
    Description: Custom feedback submission form with folowing features:
                 - form fields are body, email (from Feedback model),
                   and an additional honeypot field.
                 - honepot field label, 'website, was chosen to attract maximum
                   spam.
    
    Author:       
    """

    # use a label that attracts maximum spam, such as 'website'
    honeypot = forms.CharField(max_length=100, label="Website", required=False)

    class Meta:
        model = Feed
        fields = ('body', 'sync',)
        widgets = {
            'body': forms.Textarea(
                attrs={'cols': 60, 'rows': 10,
                       'placeholder': 'leave your message here'}),
        }

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)

    def clean_honeypot(self):
        """
        Description: Confirm that honeypot field is indeed empty. If it isn't
                     then this form submission is invalid and likely spam.
        
        Arguments:   None
        Return:      cleaned honeypot field data
        
        Author:        
        """
        honeypot = self.cleaned_data.get('honeypot', False)
        if honeypot:
            raise forms.ValidationError("You are a bot.")

        return honeypot
