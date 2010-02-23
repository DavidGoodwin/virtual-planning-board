from django.views.generic.simple import direct_to_template
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from board.models import *

def index(request):
    """
    Displays a list of all available projects, allowing the user to pick one.
    """
    
    projects = Project.objects.getAllProjectNames()
    data = {'projects': projects, 'allow_all_projects': False}
    return direct_to_template(request, 'reporting/choose-project.html', data)

def choose_details(request, project_name, error = ''):
    """
    Once a project has been selected, this allows the user to choose which developer, which ticket type and the dates
    between which the ticket should fall in to.
    """
    
    developers = []
    if project_name == 'all':
        developers = Person.objects.getAllDevelopers()
    else:
        tickets = Ticket.objects.filter(project__name = project_name)
        for ticket in tickets:
            # Only add developers who are not already in the list.
            try:
                index = developers.index(ticket.assigned_person.username)
                continue
            except ValueError:
                developers.append(ticket.assigned_person.username)
            
            # Get the names of all developers who have made changes to the ticket.
            change_authors = ticket.getChangeAuthors()
            for change_author in change_authors:
                try:
                    index = developers.index(change_author)
                    continue
                except ValueError:
                    developers.append(change_author)
        developers.sort()
    
    # Get the different types of tickets.
    ticket_types = ['defect', 'enhancement', 'task', 'support']
    
    # Pass it off to the template.
    data = {'developers': developers, 'ticket_types': ticket_types}
    if error != '':
        data['error'] = error
    return direct_to_template(request, 'reporting/choose-details.html', data)

def do_report(request, project_name):
    """
    Finds the tickets which match the data given by the user, then display the appropriate data.
    """
    
    try:
        developer = request.POST['developer']
        ticket_type = request.POST['ticket_type']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
    except KeyError, message:
        return choose_details(request, project_name, 'Missing one or more fields')
    
    # Find all changes which meet the criteria.
    tickets = Ticket.objects.fetchTickets(project_name, developer, ticket_type, start_date, end_date)
    
    data = {'developer': developer, 'project_name': project_name, 'tickets': tickets, 'path_to_trac': settings.PATH_TO_TRAC}
    return direct_to_template(request, 'reporting/time-spent-report.html', data)
