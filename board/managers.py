from django.contrib.auth.models import UserManager
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

class PersonManager(UserManager):
    def __init__(self):
        super(PersonManager, self).__init__()

    def getAllDevelopers(self):
        names = []
        developers = super(PersonManager, self).all().order_by('username')
        for developer in developers:
            names.append(developer.username)
        return names
    
    def authenticate(self, request):
        try:
            remote_user = request.META['REMOTE_USER']
        except KeyError:
            remote_user = None
        try:
            return self.get(username=remote_user)
        except ObjectDoesNotExist:
            return None

class TicketManager(models.Manager):
    def getTicketsForProjectByName(self, project_name):
        return super(TicketManager, self).filter(project__name = project_name)
    
    def fetchTickets(self, project_name, developer, ticket_type, start_date, end_date):
        if project_name != 'all':
            changes = super(TicketManager, self).filter(project__name = project_name)
        if developer != 'all':
            changes = changes.filter(assigned_person__username = developer)
        changes = changes.filter(creation_date__gte = start_date)
        changes = changes.filter(creation_date__lte = end_date)
        changes = changes.order_by('trac_ticket_id')
        print changes.query.as_sql()
        return changes
    
    def fetchTicketsForDeveloper(self, developer_name):
        tickets = super(TicketManager, self).filter(assigned_person__username = developer_name)
        tickets = tickets.exclude(status = 'closed')
        tickets = tickets.order_by('trac_ticket_id').order_by('project__name')
        return tickets

    def getFilteredTickets(self, request, project_name, ticket_fields):
        tickets = self.getTicketsForProjectByName(project_name)
        filter_data = {}
        try:
            submit = request.POST['submit']
            filter_fields = {'filter_by': '', 'filter_criteria': '', 'filter_text': '', 'order_by_1': '', 'order_by_2': '', 'order': ''}
            valid_criteria = {'contains': '__icontains', 'equal': '', 'not_equal': '', 'greater_equal': '__gte', 'greater': '__gt', 'less': '__lt', 'less_equal': '__lte', 'is_null': '__isnull'}
            for field in filter_fields:
                filter_fields[field] = request.POST[field]

            # Validate the input.
            if filter_fields['order'] != 'ascending' and filter_fields['order'] != 'descending':
                raise ValueError
            if valid_criteria.has_key(filter_fields['filter_criteria']) != True:
                raise ValueError
            temp = ticket_fields.index(filter_fields['filter_by'])
            temp = ticket_fields.index(filter_fields['order_by_1'])
            temp = ticket_fields.index(filter_fields['order_by_2'])

            # Pass the data back to re-populate the form.
            filter_data = {'filter_by': filter_fields['filter_by'],
                'filter_criteria': filter_fields['filter_criteria'],
                'filter_text': filter_fields['filter_text'],
                'order_by_1': filter_fields['order_by_1'],
                'order_by_2': filter_fields['order_by_2'],
                'order': filter_fields['order'],
            }

            # Apply filters.
            print filter_fields['filter_criteria']
            if filter_fields['filter_text'] != '' or filter_fields['filter_criteria'] == 'is_null':
                if filter_fields['filter_criteria'] == 'is_null':
                    filter_fields['filter_text'] = True
                filter_field = filter_fields['filter_by'] + valid_criteria[filter_fields['filter_criteria']]
                filter_tuple = (filter_field, filter_fields['filter_text'])
                if filter_fields['filter_criteria'] == 'not_equal':
                    tickets = tickets.exclude(filter_tuple)
                else:
                    tickets = tickets.filter(filter_tuple)

            # Apply ordering.
            if filter_fields['order'] == 'descending':
                filter_fields['order_by_1'] = '-' + filter_fields['order_by_1']
                filter_fields['order_by_2'] = '-' + filter_fields['order_by_2']
            tickets = tickets.order_by(filter_fields['order_by_2']).order_by(filter_fields['order_by_1'])
        except:
            tickets = tickets.order_by('trac_ticket_id')
        
        return (tickets, filter_data)

class TicketChangeManager(models.Manager):
    def fetchChanges(self, project_name, developer, ticket_type, start_date, end_date):
        if project_name != 'all':
            changes = super(TicketChangeManager, self).filter(ticket__project__name = project_name)
        if developer != 'all':
            changes = changes.filter(author__username = developer)
        changes = changes.filter(change_datetime__gte = start_date)
        changes = changes.filter(change_datetime__lte = end_date)
        changes = changes.order_by('-ticket__trac_ticket_id').order_by('-change_datetime')
        return changes

class ProjectManager(models.Manager):
    def getAllProjectNames(self):
        names = []
        projects = super(ProjectManager, self).all().order_by('name')
        for project in projects:
            names.append(project.name)
        return names
