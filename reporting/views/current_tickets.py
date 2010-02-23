from django.views.generic.simple import direct_to_template
from django.conf import settings
from board.models import *

def index(request):
    """
    Displays a list of all available projects, allowing the user to pick one.
    """
    
    developers = Person.objects.getAllDevelopers()
    data = {'developers': developers, 'developer_count': len(developers)}
    return direct_to_template(request, 'reporting/current-tickets.html', data)

def do_report(request, developer_name):
    """
    Shows all tickets for the chosen developer.
    """
    
    projects = []
    tickets = Ticket.objects.fetchTicketsForDeveloper(developer_name)
    for ticket in tickets:
        try:
            if projects.index(ticket.project.name):
                continue
        except:
            projects.append(ticket.project.name)
        
    data = {'developer_name': developer_name, 'tickets': tickets, 'projects': projects, 'path_to_trac': settings.PATH_TO_TRAC}
    return direct_to_template(request, 'reporting/current-tickets-report.html', data)
