from cas.decorators import gateway
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
@login_required
def index(request):
    user = request.user
    print user.get_all_permissions()
    return HttpResponse('THIS IS WILL. <br> YOU ARE IN MONITATION!')