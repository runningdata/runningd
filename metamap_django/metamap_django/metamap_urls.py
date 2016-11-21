"""metamap_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from cas import views
from django.conf.urls import include, url
from django.contrib import admin

from will_common.views import common

urlpatterns = [
    url(r'^$', common.redir_metamap),
    url(r'^export/', include('metamap.xcurls')),
    url(r'^metamap/', include('metamap.urls', namespace='metamap')),
    url(r'^admin/', admin.site.urls),

    # CAS
    # url(r'^accounts/login/$', views.login, name='login'),
    # url(r'^accounts/logout/$', views.logout, name='logout'),
]


handler500 = 'will_common.views.common.h500'

# handler404 = 'metamap.views.common.h404'