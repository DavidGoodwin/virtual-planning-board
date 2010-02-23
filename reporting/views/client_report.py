from django.views.generic.simple import direct_to_template
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.conf import settings
from board.models import *
from board.managers import PersonManager
from reporting.forms import CostForm

def index(request):
    """
    Displays a list of all available projects, allowing the user to pick one.
    """
    
    # If they're logged in and their name matches a project, direct them to it, because we don't want to give them the
    # option of viewing other projects. Only admins should see all projects. Denied to the rest.
    person = Person.objects.authenticate(request)
    if person == None:
        return HttpResponseRedirect('/') # Should never happen.
    if not person.is_staff:
        return HttpResponseRedirect('/reporting/client-report/' + person.username + '/')
    
    projects = Project.objects.getAllProjectNames()
    data = {'projects': projects, 'allow_all_projects': False}
    return direct_to_template(request, 'reporting/choose-project.html', data)

def do_report(request, project_name):
    """
    Finds the tickets which match the data given by the user, then displays the appropriate data.
    """
    
    # Check that the project name matches their user name, since we don't want to allow them to view other projects.
    person = Person.objects.authenticate(request)
    if person == None:
        return HttpResponseRedirect('/') # Should never happen.
    if not person.is_staff and project_name != person.username:
        return HttpResponseRedirect('/reporting/client-report/')
    
    can_edit = False
    if person.is_staff:
        can_edit = True
    
    ticket_fields = ['trac_ticket_id', 'title', 'description', 'status', 'creation_date']
    result = Ticket.objects.getFilteredTickets(request, project_name, ticket_fields)
    tickets = result[0]
    filter_data = result[1]
    
    # Tally up the votes to see who won.
    total_hours = 0
    total_cost = 0
    for ticket in tickets:
        total_hours = total_hours + ticket.actual_time
        total_cost = total_cost + ticket.getCostSoFar()
    
    # Whether or not the "Time Spent" column should be shown.
    show_time_spent = False
    if len(tickets) > 0:
        show_time_spent = tickets[0].project.show_total_hours
    
    data = {'tickets': tickets,
        'ticket_count': len(tickets),
        'total_hours': total_hours,
        'total_cost': total_cost,
        'project_name': project_name,
        'show_time_spent': show_time_spent,
        'can_edit': can_edit,
        'filter_data': filter_data,
        'path_to_trac': settings.PATH_TO_TRAC,
    }
    return direct_to_template(request, 'reporting/client-report.html', data)

def edit_ticket(request, project_name, trac_ticket_id):
    """
    Allows users to edit the cost of tickets.
    """
    
    person = Person.objects.authenticate(request)
    if person == None:
        return HttpResponseRedirect('/') # Should never happen.
    if not person.is_staff:
        return HttpResponseRedirect('/reporting/client-report/' + person.username + '/')
    
    try:
        ticket = Ticket.objects.get(project__name = project_name, trac_ticket_id = trac_ticket_id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect('/reporting/client-report/' + project_name + '/')
    
    # Handle the form.
    if request.method == 'POST':
        form = CostForm(request.POST)
        if form.is_valid():
            if ticket.cost != None:
                print "Existing cost"
                ticket.cost.per_hour = form.cleaned_data['per_hour']
                ticket.cost.override_total = form.cleaned_data['override_total']
                ticket.cost.save()
            else:
                print "New cost"
                cost = Cost()
                cost.per_hour = form.cleaned_data['per_hour']
                cost.override_total = form.cleaned_data['override_total']
                cost.save()
                ticket.cost = cost
            
            ticket.save()
            return HttpResponseRedirect('/reporting/client-report/' + project_name + '/')
    else:
        cost = ticket.cost
        if cost == None:
            cost = Cost()
        form = CostForm(instance = cost)
    
    data = {'ticket': ticket, 'form': form, 'project_name': project_name}
    return direct_to_template(request, 'reporting/client-report-ticket-edit.html', data)
