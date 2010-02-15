import datetime
from django.db import models
from django.contrib.auth.models import User
from planner.board.managers import PersonManager, ProjectManager, TicketManager, TicketChangeManager

class Cost(models.Model):
    per_hour = models.FloatField(default = 0)
    override_total = models.FloatField(default = 0)

class Person(User):
    default_hours_per_day = models.FloatField(default=0)
    objects = PersonManager()

class Project(models.Model):
    name = models.CharField(max_length=500)
    colour = models.CharField(max_length=6)
    cost_per_hour = models.FloatField(default = 0)
    show_total_hours = models.BooleanField()
    
    def coloured(self):
        return u'<span style="color: #%s;">%s</span>' % (self.colour, self.colour)
    
    coloured.allow_tags = True
    coloured.admin_order_field = 'colour'
    objects = ProjectManager()
    
    def __unicode__(self):
        return self.name

class ProjectAlias(models.Model):
    project_id = models.IntegerField()
    name = models.CharField(max_length=500)

class Week(models.Model):
    start_date = models.DateField()

    def __unicode__(self):
        return self.start_date.isoformat()

    def getUnFixedTickets(self):
        tickets = Ticket.objects.filter(week__id=self.id)
        tickets = tickets.exclude(status='closed')
        tickets = tickets.order_by('priority')
        if tickets.count() > 0:
            self.hasUnFixedTickets = True
        else: 
            self.hasUnFixedTickets = False
        return tickets

    def hasUnFixedTickets(self):
        return self.hasUnFixedTickets

    def isCurrentWeek(self):
        today = datetime.date.today()
        weekday = today.weekday()
        start = today - datetime.timedelta(days=weekday)
        if start == self.start_date:
            return True
        return False
    isCurrentWeek.boolean = True
    isCurrentWeek.short_description = 'Current Week'

    def getTotalAvailableHours(self):
        person_time = WeekDayPersonHours.objects.filter(week__id=self.id)
        hours = 0
        for time in person_time:
            hours += time.available_hours
        return hours

    def getTotalAvailableHoursLink(self):
        hours = self.getTotalAvailableHours()
        return u'<a href="%s/view/">%s</a>' % (self.id, hours)
    getTotalAvailableHoursLink.short_description = 'Total Available Hours'
    getTotalAvailableHoursLink.allow_tags = True

    def getAvailableHours(self):
        hours = 0
        if self.isCurrentWeek():
            today = datetime.date.today()
            weekday = today.weekday()
            person_time = WeekDayPersonHours.objects.filter(week__id=self.id).filter(day__gte=weekday)
            for time in person_time:
                hours += time.available_hours
            return hours
        else:
            return self.getTotalAvailableHours()
    
    def getTotalEstimatedTicketTimes(self):
        assigned_hours = 0
        tickets = self.getUnFixedTickets()
        for ticket in tickets:
            assigned_hours = assigned_hours + ticket.estimated_time
        
        return assigned_hours
    
    def getTotalHoursSpent(self):
        actual_hours_spent = 0
        tickets = Ticket.objects.filter(week = self.id)
        tickets = tickets.exclude(status = 'closed')
        for ticket in tickets:
            actual_hours_spent = actual_hours_spent + ticket.actual_time
        
        return actual_hours_spent
    
    def getRemainingWorkHours(self):
        return (self.getTotalEstimatedTicketTimes() - self.getTotalHoursSpent())
    
    def getUnassignedHours(self):
        return (self.getAvailableHours() - self.getRemainingWorkHours())

class Ticket(models.Model):
    trac_ticket_id = models.IntegerField()
    project = models.ForeignKey(Project)
    title = models.CharField(max_length=500)
    description = models.TextField()
    assigned_person = models.ForeignKey(Person)
    week = models.ForeignKey(Week, null=True)
    status = models.CharField(max_length=50)
    priority = models.IntegerField()
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    accepted = models.BooleanField()
    estimated_time = models.FloatField(default=0)
    actual_time = models.FloatField(default=0)
    cost = models.ForeignKey(Cost, null=True)
    
    objects = TicketManager()
    
    def __unicode__(self):
        return self.title
    
    def getCostSoFar(self):
        cost_per_hour = 0
        if self.cost != None:
            if self.cost.override_total > 0:
                return self.cost.override_total
            else:
                cost_per_hour = self.cost.per_hour
        
        # If the cost per hour was not set in the database, get it from the settings file.
        if cost_per_hour == 0:
            cost_per_hour = self.project.cost_per_hour
        
        cost_so_far = self.actual_time * cost_per_hour
        return cost_so_far
    
    def getChangeAuthors(self):
        names = []
        changes = TicketChange.objects.filter(ticket__id = self.id).exclude(author = self.assigned_person)
        for change in changes:
            try:
                index = names.index(change.author.username)
                continue
            except ValueError:
                names.append(change.author.username)
        return names
    
    def getTimeDifference(self):
        return self.estimated_time - self.actual_time
    
class TicketChange(models.Model):
    ticket = models.ForeignKey(Ticket)
    author = models.ForeignKey(Person)
    comment = models.TextField()
    hours = models.FloatField()
    change_datetime = models.DateTimeField()
    
    objects = TicketChangeManager()

class WeekDayPersonHours(models.Model):
    week = models.ForeignKey(Week)
    person = models.ForeignKey(Person)
    available_hours = models.FloatField()
    day = models.SmallIntegerField()
