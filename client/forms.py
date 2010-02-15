from planner.board.models import Cost
from django.forms import ModelForm

class CostForm(ModelForm):
    class Meta:
        model = Cost
