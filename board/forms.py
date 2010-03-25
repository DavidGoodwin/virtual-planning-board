from board.models import Person, WeekDayPersonHours, Project
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm, ChoiceField, ValidationError
import calendar
import re

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

class ProjectForm(ModelForm):

    class Meta:
        model = Project

    def clean_colour(self):
        data = self.cleaned_data['colour']

        if not re.match("^[0-9a-fA-F]{6}$", data):
            raise ValidationError("Colour should be given in hexadecimal triplet form")

        return data
