from django.views.generic.simple import direct_to_template
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from planner.board.models import *
from planner.reporting.forms import list_to_choices, SearchTimeBookingForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def index(request):
    """
    Displays a list of all available projects, allowing the user to pick one.
    """
    
    projects = Project.objects.getAllProjectNames()
    data = {'projects': projects, 'allow_all_projects': True}
    return direct_to_template(request, 'reporting/choose-project.html', data)

def choose_details(request, project_name):
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

    if '' not in developers:
        developers.insert(0, '')

    # Get the different types of tickets.
    ticket_types = ['', 'defect', 'enhancement', 'task', 'support']
    
    SearchTimeBookingForm.base_fields['developer'].choices = list_to_choices(developers)
    SearchTimeBookingForm.base_fields['type'].choices = list_to_choices(ticket_types)

    if request.method == 'POST':
        form = SearchTimeBookingForm(request.POST)
        if form.is_valid():
            return do_report(request, project_name)
    
    else:
        form = SearchTimeBookingForm()

    data = {'form': form}

    return direct_to_template(request, 'reporting/choose-details.html', data)

def do_report(request, project_name):
    """
    Finds the tickets which match the data given by the user, then display the appropriate data.
    """
    
    try:
        developer = request.POST['developer']
        ticket_type = request.POST['type']
        start_date = request.POST['start']
        end_date = request.POST['end']
    except KeyError, message:
        url = reverse('planner.reporting.views.hours.choose_details', kwargs={'project_name': project_name})
        return HttpResponseRedirect(url)
    
    # Find all changes which meet the criteria.
    changes = TicketChange.objects.fetchChanges(project_name, developer, ticket_type, start_date, end_date)
    
    total_hours = 0
    for change in changes:
        total_hours = total_hours + change.hours
    
    data = {'developer': developer, 'project_name': project_name, 'total_hours': total_hours, 'changes': changes, 'path_to_trac': settings.PATH_TO_TRAC}
    return direct_to_template(request, 'reporting/hours-report.html', data)
