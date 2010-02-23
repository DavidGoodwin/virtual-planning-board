from django.views.generic.simple import direct_to_template
from board.plugins import PlanningBoard
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def index(request):
    """
    Displays the planning board, defaulting to display the 
    logged in user / default number of weeks.
    """
    board = PlanningBoard(request)
    data = board.fetchBoardData()
    
    return direct_to_template(request, 'board/index.html', data)

def person(request, person_id):
    """
    Changes the default user display.
    """
    request.session['person_id'] = person_id
    request.session.modified = True

    board = PlanningBoard(request)
    data = board.fetchBoardData() 

    return direct_to_template(request, 'board/index.html', data)

def weeks(request, weeks):
    """
    Changes the default weeks display.
    """
    request.session['weeks'] = weeks
    request.session.modified = True
    
    board = PlanningBoard(request)
    data = board.fetchBoardData() 

    return direct_to_template(request, 'board/index.html', data)

def redirect_to_board(request):
    index = reverse('board.views.index.index')
    return HttpResponseRedirect(index)    
