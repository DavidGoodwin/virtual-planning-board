from planner.board.models import Cost, Ticket
from django import forms

class CostForm(forms.ModelForm):
    class Meta:
        model = Cost

class SearchTimeBookingForm(forms.Form):
    developer = forms.ChoiceField(required=False)
    type = forms.ChoiceField(required=False)
    start = forms.DateField()
    end = forms.DateField()

def list_to_choices(list):
    choices = []
    for item in list:
        choices += [(item, item)]
    return choices
