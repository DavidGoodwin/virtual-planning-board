from django.conf import settings

def admin_url(request):
    admin_url = settings.ADMIN_URL
    if admin_url[-1:] == '/':
        admin_url = admin_url[:-1]
    media_url = settings.ADMIN_MEDIA_PREFIX
    
    data = {'admin_url': admin_url, 'ADMIN_MEDIA_PREFIX': media_url}
    return data
