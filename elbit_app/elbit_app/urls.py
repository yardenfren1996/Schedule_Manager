"""elbit_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from my_shifts import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.home, name='home'),
    path('admin/', admin.site.urls),
    url(r'^my_shifts/', include('my_shifts.urls', namespace='my_shifts')),
    url(r'^user_login/$', views.user_login, name='user_login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^submitting_shifts/$', views.submitting_shifts, name='submitting_shifts'),
    url(r'^send_confirm/$', views.send_confirm, name='send_confirm'),
    url(r'^create_schedule/$', views.create_schedule, name='create_schedule'),
    url(r'^approve_schedule/$', views.approve_schedule, name='approve_schedule'),
    url(r'^post_schedule/$', views.post_schedule, name='post_schedule'),
    url(r'^work_schedule/$', views.work_schedule, name='work_schedule'),
]
