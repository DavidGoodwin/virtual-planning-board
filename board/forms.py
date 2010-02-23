from board.models import Person, WeekDayPersonHours
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm, ChoiceField
import calendar

class PersonCreationForm(UserCreationForm):

    class Meta:
        model = Person
        fields = ("username",)

class PersonChangeForm(UserChangeForm):
    
    class Meta:
        model = Person

class WeekDayPersonHoursAssignForm(ModelForm):
    day = ChoiceField(choices=[(i, calendar.day_name[i]) for i in range(5)])

    class Meta:
        model = WeekDayPersonHours
