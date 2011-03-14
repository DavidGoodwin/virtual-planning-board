from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils import simplejson
from board.models import *
from math import ceil

def get_ticket_info(request, ticket_id):
    """
    It takes the ID of a ticket as a parameter and returns certain data about the ticket as JSON, which is then
    displayed to the user by some client-side Javascript.
    To be called via Ajax.
    """
    
    try:
        ticket_object = Ticket.objects.get(id = ticket_id)
    except ObjectDoesNotExist:
        return HttpResponse('No such ticket')
    
    ticket = {}
    ticket['title'] = ticket_object.title
    ticket['description'] = ticket_object.description
    ticket['owner'] = ticket_object.assigned_person.username
    ticket['project'] = ticket_object.project.name
    ticket['trac_id'] = ticket_object.trac_ticket_id
    ticket['creation_date'] = ticket_object.creation_date.strftime('%d/%m/%Y')
    ticket['est_time'] = ticket_object.estimated_time
    
    output = simplejson.dumps(ticket)
    return HttpResponse(output)



def get_unassigned_tickets(request, project_id, title, trac_id, page, limit):
    """
    Finds and returns (as JSON) all unassigned tickets. It also supports searching of the unassigned tickets.
    To be called via Ajax.
    """
    
    # Clean up the values.
    project_id = int(project_id)
    trac_id = int(trac_id)
    page = int(page)
    limit = int(limit)
    
    # Build the query.
    query = Ticket.objects.filter(week__isnull = True)
    query = query.exclude(status = 'closed')
    
    if project_id != 0:
        query = query.filter(project__id = project_id)
    if title != ' ':
        query = query.filter(title__contains = title)
    if trac_id != 0:
        query = query.filter(trac_ticket_id = trac_id)
    
    # Paginate. Kind of.
    pages = 1
    total = query.count()
    if total > limit:
        pages = ceil((total + 0.1) / limit)
    start = page * limit
    end = limit - start
    results = query[start:end]
    
    # Loop through all results.
    tickets = {'pages': pages, 'tickets': []}
    for result in results:
        ticket = {}

        title = result.title
        if len(title) > 16:
            title = title[:16] + '...'
        ticket['title'] = title
        ticket['long_title'] = result.title
        ticket['description'] = result.description
        ticket['owner'] = result.assigned_person.username
        ticket['project'] = result.project.name
        ticket['id'] = result.id
        ticket['trac_id'] = result.trac_ticket_id
        ticket['bgcolor'] = result.project.colour
        ticket['est_time'] = result.estimated_time
        
        tickets['tickets'].append(ticket)
    
    output = simplejson.dumps(tickets)
    return HttpResponse(output)



def save_ticket(request, ticket_id, priority, week_date):
    """
    Saves the ticket's position on the board.
    To be called via Ajax.
    """
    
    ticket_id = int(ticket_id)
    priority = int(priority)
    
    try:
        ticket = Ticket.objects.get(id = ticket_id)
    except ObjectDoesNotExist:
        return HttpResponse('No such ticket')
    
    try:
        week = Week.objects.get(start_date = week_date)
    except ObjectDoesNotExist:
        return HttpResponse('No such week')

    ticket.week = week
    ticket.priority = priority
    ticket.save()
    
    return HttpResponse('Saved')



def get_week_info(request, week_date):
    """
    Finds and returns the data for the given week.
    To be called via Ajax.
    """
    
    try:
        week = Week.objects.get(start_date = week_date)
    except ObjectDoesNotExist:
        data = {'success': False, 'message': 'Invalid start date provided'}
        output = simplejson.dumps(data)
        return HttpResponse(output)
    
    week_data = {}
    week_data['start_date'] = week_date
    week_data['week_avail_hours'] = week.getTotalAvailableHours()
    week_data['avail_hours_remain'] = week.getAvailableHours()
    week_data['total_est_ticket_times'] = week.getTotalEstimatedTicketTimes()
    week_data['total_hours_spent'] = week.getTotalHoursSpent()
    week_data['remain_work_hours'] = week.getRemainingWorkHours()
    week_data['unassigned_hours'] = week.getUnassignedHours()
    
    data = {'success': True, 'message': 'Week retrieved successfully', 'week': week_data}
    output = simplejson.dumps(data)
    
    return HttpResponse(output)
