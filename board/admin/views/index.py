from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from board.models import Week, WeekDayPersonHours, Person
from datetime import datetime
from board.forms import WeekDayPersonHoursAssignForm
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required

def index(request, week_id):
    """
    Displays a breakdown of the developer hours per day
    """

    today = datetime.now()
    
    data = {}
    data['title'] = 'View Week'
    data['week'] = get_object_or_404(Week, pk=week_id)
    data['days'] = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri'}
    data['current'] = today.isoweekday() - 1

    return direct_to_template(request, 'admin/board/week/view.html', data)
index = staff_member_required(index)

def assign(request, week_id):
    """
    Assigns a person to a week
    """
    week = get_object_or_404(Week, pk=week_id)
    
    if request.method == 'POST':
        form = WeekDayPersonHoursAssignForm(request.POST)
        if form.is_valid():
            form.save()
            
            return HttpResponseRedirect('../view/')
    else:
        person_hours = WeekDayPersonHours()
        person_hours.week = week
        form = WeekDayPersonHoursAssignForm(instance=person_hours)

    data = {}
    data['title'] = 'Assign Week'
    data['form'] = form
    data['week'] = week

    return direct_to_template(request, 'admin/board/week/assign.html', data)
assign = staff_member_required(assign)

def edit(request, week_id, hours_id):
    """
    Edits a person assigned to a week
    """
    week = get_object_or_404(Week, pk=week_id)
    person_hours = get_object_or_404(WeekDayPersonHours, pk=hours_id)

    if request.method == 'POST':
        form = WeekDayPersonHoursAssignForm(request.POST, instance=person_hours)
        if form.is_valid():
            form.save()
            
            return HttpResponseRedirect('../../view/')
    else:
        form = WeekDayPersonHoursAssignForm(instance=person_hours)

    data = {}
    data['title'] = 'Edit Assignment'
    data['form'] = form
    data['week'] = week

    return direct_to_template(request, 'admin/board/week/assign.html', data)
edit = staff_member_required(edit)

def populate(request, week_id):
    """
    (re)Populates Week with all people and their default hours
    """
    week = get_object_or_404(Week, pk=week_id)

    persons_hours = WeekDayPersonHours.objects.filter(week=week)

    for hours in persons_hours:
        hours.delete()

    persons = Person.objects.all()

    for person in persons:
        for day in range(0, 5):
            person_hours = WeekDayPersonHours()
            person_hours.week = week
            person_hours.person = person
            person_hours.available_hours = person.default_hours_per_day
            person_hours.day = day
            person_hours.save()

    return HttpResponseRedirect('../view/')
populate = staff_member_required(populate)
