from planner.board.models import Project, Person, Ticket, Week
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, timedelta
from calendar import monthrange

class PlanningBoard(object):
    data = {}
    personId = 0
    weeks = 4

    def __init__(self, request):
        self.today = date.today()

        try:
            remote_user = request.META['REMOTE_USER']
        except KeyError:
            remote_user = None

        try:
            person = Person.objects.get(username=remote_user)
            user_id = person.id
        except ObjectDoesNotExist:
            user_id = request.user.id

        person_id = request.session.get('person_id', user_id)
        weeks = request.session.get('weeks', self.weeks)

        self.setPersonId(person_id)
        self.setNumberOfWeeks(weeks)

    def setPersonId(self, person_id):
        self.personId = self.fetchIntValue(person_id)

    def setNumberOfWeeks(self, number):
        self.weeks = self.fetchIntValue(number)
   
    def fetchIntValue(self, number):
        if type(number) == int:
            return number
        elif type(number) == unicode and number.isnumeric():
            return int(number)
    
    def getStartOfCurrentWeek(self):
        weekday = self.today.weekday()
        start = self.today - timedelta(days=weekday)
        return start

    def getEndOfTheMonth(self):
        last = monthrange(self.today.year, self.today.month)[1]
        end = date(self.today.year, self.today.month, last)
        return end

    def fetchBoardData(self):
        start = self.getStartOfCurrentWeek()
        end = self.getEndOfTheMonth()

        self.data['projects'] = Project.objects.order_by('name')
        self.data['people'] = Person.objects.order_by('username')
        self.data['person_id'] = self.personId

        weekday = self.today.strftime('%a')
        if weekday == 'Sat' or weekday == 'Sun':
            range = u'Mon-Fri'
        elif weekday == 'Fri':
            range = u'Fri';
        else:
            range = u'%s-Fri' % weekday
        
        self.data['week_range'] = range

        try:
            person = Person.objects.get(pk=self.personId)
            self.data['username'] = person.username
        except ObjectDoesNotExist:
            self.data['username'] = u'All'

        homeless = Ticket.objects.exclude(status='closed')
        homeless = homeless.filter(week__start_date__lt=start)
        self.data['homeless'] = homeless.order_by('priority')

        weeks = Week.objects.filter(start_date__gte=start)
        weeks = weeks.order_by('start_date')
        
        if self.weeks == 0:
            weeks = weeks.filter(start_date__lte=end)

        if self.weeks > 0:
            weeks = weeks[:self.weeks]

        self.data['weeks'] = weeks

        return self.data
