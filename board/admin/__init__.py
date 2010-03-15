from board.models import Person, Project, Ticket, Week
from django.contrib import admin
from board.widgets import ReadOnlyAdminFields
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext, ugettext_lazy as _
from board.forms import PersonChangeForm, PersonCreationForm

class ProjectAdmin(admin.ModelAdmin):
    fields = ('name', 'colour')
    list_display = ('name', 'coloured')
    ordering = ('name',)
    list_per_page = 25
    search_fields = ('id', 'name', 'colour')

class TicketAdmin(admin.ModelAdmin):
    fields = ('title', 'trac_ticket_id', 'project', 'description', 'estimated_time', 'assigned_person', 'week')
    #fields_read_only = ('title', 'trac_ticket_id', 'project', 'description', 'estimated_time', 'assigned_person') 
    list_display = ('project', 'trac_ticket_id', 'title', 'estimated_time', 'assigned_person', 'week')
    list_filter = ('project',)
    ordering = ('-week__start_date', )
    list_per_page = 25
    search_fields = ('project__name', 'trac_ticket_id', 'title', 'estimated_time', 'assigned_person__username', 'week__start_date')

    class Media:
        css =  {
            'all': ('admin/css/forms/ticket.css',)
        }

class PersonAdmin(UserAdmin):
    list_display = ('username', 'default_hours_per_day')
    list_filter = ()
    list_per_page = 25
   
    fieldsets = ( 
        (None, {'fields': ('username', 'password')}),
        ('Hours', {'fields': ('default_hours_per_day', )}),
    )   
    
    form = PersonChangeForm
    add_form = PersonCreationForm

    def queryset(self, request):
        qs = super(PersonAdmin, self).queryset(request)
        qs = qs.filter(is_staff=0)

        return qs

class WeekAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ('start_date', 'isCurrentWeek', 'getTotalAvailableHoursLink', )
    search_fields = ('start_date',)
    ordering = ('-start_date',)

class CustomUserAdmin(UserAdmin):

    def queryset(self, request):
        qs = super(CustomUserAdmin, self).queryset(request)
        qs = qs.filter(is_staff=1)

        return qs

admin.site.register(Person, PersonAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Week, WeekAdmin)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
