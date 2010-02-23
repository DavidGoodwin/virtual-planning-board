import datetime
from django.http import HttpResponse
from board.models import Week, Person, WeekDayPersonHours

def index(request):
    """
    Keeps the "week" table populated with plenty of weeks.
    """
    
    days_per_week = 5
    number_of_weeks = 6
    weekday_number = (datetime.datetime.isoweekday(datetime.date.today()) - 1)
    week_start = datetime.date.today() - datetime.timedelta(weekday_number)
    
    # Do we need to create any new weeks, or are there already enough?
    weeks = Week.objects.filter(start_date__gte = week_start)
    if len(weeks) >= number_of_weeks:
        return HttpResponse('OK')
    
    # Not enough weeks in the database, so create some.
    developers = Person.objects.all()
    if len(weeks) > 0:
        week_start = weeks[len(weeks) - 1].start_date + datetime.timedelta(7)
    
    for i in range(0, (6 - len(weeks))):
        new_week = Week(start_date = week_start)
        new_week.save()
        week_start = week_start + datetime.timedelta(7)
        
        # Add developer hours to each week.
        for developer in developers:
            for day in range(0, days_per_week):
                week_day_person_hours = WeekDayPersonHours()
                week_day_person_hours.week = new_week
                week_day_person_hours.person = developer
                week_day_person_hours.available_hours = developer.default_hours_per_day
                week_day_person_hours.day = day
                week_day_person_hours.save()
    
    return HttpResponse('OK')
