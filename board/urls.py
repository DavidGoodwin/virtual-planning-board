from django.conf.urls.defaults import *

urlpatterns = patterns('board.views',
    (r'^$', 'index.index'),
    (r'^person/(?P<person_id>\d+)/', 'index.person'),
    (r'^weeks/(?P<weeks>\d+)/', 'index.weeks'),
    (r'^ping/', 'ping.index'),
    (r'^week-info/(?P<week_date>[a-zA-Z0-9\-]*)/', 'ajax.get_week_info'),
    (r'^ticket-info/(?P<ticket_id>\d+)/', 'ajax.get_ticket_info'),
    (r'^save-ticket/(?P<ticket_id>\d+)/(?P<priority>\d+)/(?P<week_date>[a-zA-Z0-9\-]*)/', 'ajax.save_ticket'),
    (r'^unassigned-tickets/(?P<project_id>\d+)/(?P<title>[a-zA-Z0-9\ \-_]*)/(?P<trac_id>\d+)/(?P<page>\d+)/(?P<limit>\d+)/', 'ajax.get_unassigned_tickets'),
    (r'^cron/$', 'cron.index'),
)

