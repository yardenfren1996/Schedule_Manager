from django.conf.urls import url
from my_shifts import views

app_name = 'my_shifts'

urlpatterns = [
    url(r'^register/$', views.register, name='register'),
    url(r'^user_login/$', views.user_login, name='user_login'),


]


