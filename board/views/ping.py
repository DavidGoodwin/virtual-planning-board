import sys, datetime, time
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from planner.board.models import Ticket, TicketChange, Project, ProjectAlias, Person

class Logger:
    filename = '/tmp/board_ping.debug'
    logFile = None

    def debug(self, message):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logFile = open(self.filename, 'a')
        self.logFile.write(now + ' >> ' + str(message) + "\n")
        self.logFile.flush()
        self.logFile.close()

# Stuff passed in from trac-python plugin thing in $_POST looks like:
# 
# [action] => changed
# [project] => Virtual Planner
# [trac_id] => 1
# [owner] => david
# [type] => defect
# [status] => assigned
# [title] => test
# [desc] => test
# [ticket_url] => https://virtual-planner.palepurple.co.uk/ticket/1
# [estimated_hours] => 12.00
# [total_hours] => 2.00
# [comment] => See #1. Changed X and Y.     # Only passed in when the ticket is changed.
# [author] => david                         # Only passed in when the ticket is changed.
# [change_time] => 1234779297               # Only passed in when the ticket is changed.
# [change_hours] => 1.0                     # Only passed in when the ticket is changed.

def index(request):
    """
    Handles the calls from the Trac plug-in, which sends data about newly created or changed tickets.
    It updates the database with that information so that the planning board is always up to date.
    """
    
    logger = Logger()
    logger.debug("\n\n-----");
    # Only pay attention to certain actions.
    actions = ['changed', 'created', 'deleted']
    try:
        action = request.POST['action']
        logger.debug('Action: ' + str(action))
    except KeyError:
        logger.debug('Missing "action" fields')
        return HttpResponse('Missing "action" fields')
    if action not in actions:
        logger.debug('Invalid action')
        return HttpResponse('Invalid action')
    
    # Make sure that all of the required data has been supplied.
    data = {'project': '', 'trac_id': '', 'owner': '', 'type': '', 'status': '', 'title': '', 'desc': '', 'ticket_url': '', 'estimated_hours': '', 'total_hours': ''}
    try:
        for field in data.keys():
            data[field] = request.POST[field]
    except KeyError:
        logger.debug('KeyError. Could not find "' + str(field) + '" in data.keys')
        return HttpResponse('Missing one or more fields')
    try:
        data['change_time'] = int(time.time())
        data['change_hours'] = 0.0
        data['comment'] = request.POST['comment']
        data['author'] = request.POST['author']
        data['change_time'] = request.POST['change_time']
        data['change_hours'] = request.POST['change_hours']
    except KeyError:
        pass
    logger.debug('Got data:' + str(data))
    
    accepted = False
    if data['status'] == 'assigned':
        accepted = True
    
    # Find ID of the ticket owner.
    try:
        person = Person.objects.get(username = data['owner'])
        logger.debug('Found person')
    except ObjectDoesNotExist:
        person = Person.objects.create_user(data['owner'], '', None)
        person.is_active = False
        person.save()
        logger.debug('Created new person')
    
    # Find the project name.
    project_name = data['project']
    if project_name == '':
        project_name = data['ticket_url'].split('/')[-3]
    logger.debug('Got project name')

    # Find the ID of the project.
    project = None
    try:
        project = Project.objects.get(name = project_name)
    except ObjectDoesNotExist:
        try:
            project = ProjectAlias.objects.get(name = project_name)
        except ObjectDoesNotExist:
            pass
    
    # If no project was found, create a new one.
    if project == None:
        project = Project(name = project_name, colour = 'FFAAFF')
        project.save()
        logger.debug('Created new project')
    
    # Check if it is an update to an existing ticket.
    try:
        ticket = Ticket.objects.get(trac_ticket_id = data['trac_id'], project = project)
        logger.debug('Found existing ticket to update')
    except ObjectDoesNotExist:
        ticket = Ticket()
        ticket.trac_ticket_id = data['trac_id']
        ticket.project = project
        ticket.week = None
        ticket.priority = 0
        logger.debug('Created new ticket')
    
    # Set properties and save.
    ticket.assigned_person = person
    ticket.type = data['type']
    ticket.status = data['status']
    ticket.title = data['title']
    ticket.description = data['desc']
    ticket.accepted = accepted
    ticket.estimated_time = data['estimated_hours']
    ticket.actual_time = data['total_hours']
    if data['status'] == 'reopened':
        ticket.week = None
        ticket.priority = 0
    ticket.save()
    logger.debug('Ticket saved')
    
    # Handle the ticket change record.
    if data.has_key('comment') and data.has_key('author'):
        # Make sure that the developer who made the change is in the system.
        try:
            author = Person.objects.get(username = data['author'])
        except ObjectDoesNotExist:
            logger.debug("Creating author...")
            author = Person.objects.create_user(data['author'], '', None)
            author.is_active = False
            author.save()
            logger.debug("Saved new author") 
       
        # Save the change to the database.
        try:
            change = TicketChange()
            change.ticket = ticket
            change.author = author
            change.comment = data['comment']
            change.hours = float(data['change_hours'])
            change.change_datetime = datetime.datetime.fromtimestamp(int(data['change_time']))
            change.save()
        except Exception, e:
            logger.debug("Exception - failed to create ticket change: " + str(e))
    logger.debug("All good") 
    return HttpResponse('Ticket change accepted')
