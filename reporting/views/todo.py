from django.views.generic.simple import direct_to_template
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.conf import settings
from planner.board.models import *

def index(request):
    """
    Displays a list of all available projects, allowing the user to pick one.
    """
    
    projects = Project.objects.getAllProjectNames()
    data = {'projects': projects, 'project_count': len(projects)}
    return direct_to_template(request, 'reporting/todo.html', data)

def action(request):
    """
    Redirect the user to the Trac instance for the chosen project.
    """
    
    project = ''
    try:
        project = request.POST['project_name']
        if request.POST.has_key('new_ticket'):
            action = 'new'
        elif request.POST.has_key('view_tickets'):
            action = 'view'
    except:
        pass
    
    if project != '':
        if action == 'new':
            return HttpResponseRedirect(settings.PATH_TO_TRAC + project + '/newticket')
        elif action == 'view':
            return HttpResponseRedirect(settings.PATH_TO_TRAC + project + '/report/1')
    
    return HttpResponseRedirect('/reporting/todo/')
