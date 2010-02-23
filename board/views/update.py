from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from board.models import *
from django.contrib.auth.models import User
from django.conf import settings
from django.db import connection
from django.db import transaction


def index(request):
    """
    Handles the calls from the Trac plug-in, which sends data about newly created or changed tickets.
    It updates the database with that information so that the planning board is always up to date.
    """

    _import_path = 'django.db.backends.'
    backend = __import__('%s%s.base' % (_import_path, settings.DATABASE_ENGINE), {}, {}, [''])

    db = backend.DatabaseWrapper()
    settings.DATABASE_NAME = "virtual-planner"

    old = db.cursor()

    old.execute("SELECT * FROM person ORDER BY id")

    settings.DATABASE_NAME = "virtual-planner-django"

    log = []

    people_ids = {}
    people = old.fetchall()
    for person in people:
        new_person = Person.objects.create_user(person[1], '', None)
        new_person.is_active = False
        new_person.default_hours_per_day = person[3]
        
        try:
            new_person.save()
            transaction.commit()
            people_ids[person[0]] = new_person.id
        except Exception, e:
            log += ['problem saving user with original id %s : %s' % (person[0], e)]
            transaction.rollback()
    
    if people[0]:
        admin = Person.objects.get(pk=people[0][0])
        admin.set_password(people[0][1])
        admin.is_active = True
        admin.is_staff = True
        admin.is_superuser = True
        
        try:
            admin.save()
            transaction.commit()
        except Exception, e:
            log += ['problem saving user with original id %s : %s' % (people[0][0], e)]
            transaction.rollback()


    old.execute("SELECT * FROM project ORDER BY id")

    project_ids = {}
    projects = old.fetchall()
    for project in projects:
        new_project = Project()
        new_project.name = project[1]
        new_project.colour = project[2]
        
        try:
            new_project.save()
            transaction.commit()
            project_ids[project[0]] = new_project.id
        except Exception, e:
            log += ['problem saving project with original id %s : %s' % (project[0], e)]
            transaction.rollback()


    old.execute("SELECT * FROM week ORDER BY id")

    week_ids = {}
    weeks = old.fetchall()
    for week in weeks:
        new_week = Week()
        new_week.start_date = week[1] 
        
        try:
            new_week.save()
            transaction.commit()
            week_ids[week[0]] = new_week.id
        except Exception, e:
            log += ['problem saving week with original id %s : %s' % (week[0], e)]
            transaction.rollback()


    old.execute("SELECT * FROM cost ORDER BY id")

    cost_ids = {}
    costs = old.fetchall()
    for cost in costs:
        new_cost = Cost()
        new_cost.per_hour = cost[1]
        new_cost.override_total = cost[2]
        
        try:
            new_cost.save()
            transaction.commit()
            cost_ids[cost[0]] = new_cost.id
        except Exception, e:
            log += ['problem saving cost with original id %s : %s' % (cost[0], e)]
            transaction.rollback()


    old.execute("SELECT * FROM week_day_person_hours ORDER BY week_day_person_hours_id")

    person_hours = old.fetchall()
    for time in person_hours:
        new_time = WeekDayPersonHours()

        try:
            new_time.week_id = week_ids[time[1]]
        except Exception, e:
            log += ['problem finding related week for time id %s for original time %s' % (time[1], time[0])]
            continue
            
        new_time.person_id = people_ids[time[2]]
        new_time.available_hours = time[3]
        new_time.day = time[4]
        
        try:
            new_time.save()
            transaction.commit()
        except Exception, e:
            log += ['problem saving time with original id %s : %s' % (time[0], e)]
            transaction.rollback()

    old.execute("SELECT * FROM ticket ORDER BY id")

    tickets = old.fetchall()
    for ticket in tickets:
        new_ticket = Ticket()
        new_ticket.trac_ticket_id = ticket[1]
        
        try:
            new_ticket.project_id = project_ids[ticket[2]]
        except Exception, e:
            log += ['problem finding related project for ticket with id %s for original ticket %s' % (ticket[2], ticket[0])]
            continue

        new_ticket.title = ticket[3]
        new_ticket.description = ticket[4]
        new_ticket.assigned_person_id = ticket[5]
        
        try:
            if ticket[6] is not None:
                new_ticket.week_id = week_ids[ticket[6]]
        except Exception, e:
            log += ['problem finding related week for ticket with id %s for original ticket %s' % (ticket[6], ticket[0])]
            continue

        new_ticket.status = ticket[7]
        new_ticket.priority = ticket[8]
        new_ticket.creation_date = ticket[9]
        new_ticket.accepted = ticket[10]

        if ticket[11] is not None:
            new_ticket.estimated_time = ticket[11]
        if ticket[12] is not None:
            new_ticket.actual_time = ticket[12]

        try:
            if ticket[13] is not None:
                new_ticket.cost_id = cost_ids[ticket[13]]
        except Exception, e:
            log += ['problem finding related cost for ticket with id %s for original ticket %s' % (ticket[13], ticket[0])]
            continue

        try:
            new_ticket.save()
            transaction.commit()
        except Exception, e:
            log += ['problem saving ticket with original id %s : %s' % (ticket[0], e)]
            transaction.rollback()

    return HttpResponse('Imported all data: ' + str(log))

index = transaction.commit_manually(index)
