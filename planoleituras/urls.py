from django.conf.urls import url

from . import views

app_name = 'planoleituras'
urlpatterns = [
	url(r'^$', views.index, name='index'),
]