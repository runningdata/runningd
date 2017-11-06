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
from django.contrib.auth.decorators import login_required

from will_common.views import common

urlpatterns = [
    url(r'^common/', include('will_common.urls')),
    url(r'^export/', include('metamap.url.xcurls')),
    url(r'^clean/', include('metamap.url.clean_urls')),
    url(r'^nosecure/', include('metamap.url.nosecure')),
    url(r'^meta/', include('metamap.url.meta')),
    url(r'^hadmin/', include('metamap.url.hadmin')),
    url(r'^hooks/', include('metamap.url.hooks')),
    url(r'^metamap/', include('metamap.url.urls', namespace='metamap')),
    url(r'^admin/', admin.site.urls),

    # CAS
    url(r'^accounts/login/$', views.login, name='login'),
    url(r'^accounts/logout/$', views.logout, name='logout'),

    # Navigate
    url(r'^$', login_required(common.navigate), name='navigate'),
    url(r'^user/$', login_required(common.modify_pwd), name='modify_pwd'),

]

handler500 = 'will_common.views.common.h500'

# handler404 = 'metamap.views.common.h404'
