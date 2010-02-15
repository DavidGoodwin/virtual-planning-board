from django.conf.urls.defaults import *

urlpatterns = patterns('planner.reporting.views',
    (r'^$', 'index.index'),
    (r'^hours/$', 'hours.index'),
    (r'^hours/(?P<project_name>[a-zA-Z0-9\ \-_]*)/$', 'hours.choose_details'),
    (r'^hours/(?P<project_name>[a-zA-Z0-9\ \-_]*)/report/$', 'hours.do_report'),
    (r'^time-spent/$', 'time_spent.index'),
    (r'^time-spent/(?P<project_name>[a-zA-Z0-9\ \-_]*)/$', 'time_spent.choose_details'),
    (r'^time-spent/(?P<project_name>[a-zA-Z0-9\ \-_]*)/report/$', 'time_spent.do_report'),
    (r'^client-report/$', 'client_report.index'),
    (r'^client-report/(?P<project_name>[a-zA-Z0-9\ \-_]*)/$', 'client_report.do_report'),
    (r'^client-report/(?P<project_name>[a-zA-Z0-9\ \-_]*)/(?P<trac_ticket_id>\d+)/$', 'client_report.edit_ticket'),
    (r'^work-todo/$', 'work_todo.index'),
    (r'^work-todo/(?P<project_name>[a-zA-Z0-9\ \-_]*)/$', 'work_todo.do_report'),
    (r'^current-tickets/$', 'current_tickets.index'),
    (r'^current-tickets/(?P<developer_name>[a-zA-Z0-9\ \-_]*)/$', 'current_tickets.do_report'),
    (r'^todo/$', 'todo.index'),
    (r'^todo/action/$', 'todo.action'),
)

