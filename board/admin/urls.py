from django.conf.urls.defaults import *

urlpatterns = patterns('board.admin.views',
    (r'^board/week/(?P<week_id>\d+)/view/$', 'index.index'),
    (r'^board/week/(?P<week_id>\d+)/assign/$', 'index.assign'),
    (r'^board/week/(?P<week_id>\d+)/assign/(?P<hours_id>\d+)/$', 'index.edit'),
    (r'^board/week/(?P<week_id>\d+)/populate/', 'index.populate')
)
