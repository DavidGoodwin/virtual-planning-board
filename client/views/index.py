from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def index(request):
    url = reverse('planner.client.views.report.index')
    return HttpResponseRedirect(url);
