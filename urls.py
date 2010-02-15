from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'planner.board.views.index.redirect_to_board'),
    (r'^board/', include('planner.board.urls')),
    (r'^reporting/', include('planner.reporting.urls')),
    (r'^client/', include('planner.client.urls')),
    (r'^admin/', include('planner.board.admin.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
