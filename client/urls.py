from django.conf.urls.defaults import *

urlpatterns = patterns('client.views',
    (r'^$', 'index.index'),
    (r'^report/$', 'report.index'),
    (r'^report/(?P<project_name>[a-zA-Z0-9\ \-_]*)/$', 'report.do_report'),
    (r'^report/(?P<project_name>[a-zA-Z0-9\ \-_]*)/(?P<trac_ticket_id>\d+)/$', 'report.edit_ticket'),
)

