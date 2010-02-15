from django.views.generic.simple import direct_to_template
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from planner.board.models import *

def index(request):
    """
    Displays a list of all available projects, allowing the user to pick one.
    """
    
    projects = Project.objects.getAllProjectNames()
    data = {'projects': projects, 'allow_all_projects': False}
    return direct_to_template(request, 'reporting/choose-project.html', data)

def do_report(request, project_name):
    """
    Show a list of tickets that are open.
    """
    
    ticket_fields = ['trac_ticket_id', 'title', 'description', 'status', 'creation_date']
    result = Ticket.objects.getFilteredTickets(request, project_name, ticket_fields)
    tickets = result[0].exclude(status__in = ['closed', 'duplicate', 'invalid'])
    filter_data = result[1]
    
    data = {'project_name': project_name, 'tickets': tickets, 'ticket_count': len(tickets), 'path_to_trac': settings.PATH_TO_TRAC, 'filter_data': filter_data}
    return direct_to_template(request, 'reporting/work-todo.html', data)
