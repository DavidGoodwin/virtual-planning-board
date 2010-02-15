from planner.board.models import WeekDayPersonHours
from django.template import Library, Node, TemplateSyntaxError

register = Library()

def get_week_day_person_hours(parser, token):
    """
    {% get_week_day_person_hours %}
    """
    bits = token.split_contents()
    if len(bits) != 3:
        raise TemplateSyntaxError, "get_week_day_person_hours tag takes exactly two arguments"
    if bits[1] != 'as':
        raise TemplateSyntaxError, "second argument to get_week_day_person_hours tag must be 'as'"
    return fetchWeekDayPersonHours(bits[2])

class fetchWeekDayPersonHours(Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        person_hours = WeekDayPersonHours.objects.filter(day=context['day'])
        person_hours = person_hours.filter(week=context['week'])
        context[self.varname] = person_hours.order_by('-available_hours') 
        return ''

register.tag(get_week_day_person_hours)
