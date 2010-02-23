from board.models import Person, WeekDayPersonHours
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm

class PersonCreationForm(UserCreationForm):

    class Meta:
        model = Person
        fields = ("username",)

class PersonChangeForm(UserChangeForm):
    
    class Meta:
        model = Person

class WeekDayPersonHoursAssignForm(ModelForm):

    class Meta:
        model = WeekDayPersonHours
