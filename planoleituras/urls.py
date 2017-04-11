from django.conf.urls import url

from . import views

app_name = 'planoleituras'
urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^(?P<tag_id>[0-9]+)/$', views.detalhe, name='detalhe'),
	url(r'^(?P<tag_id>[0-9]+)/atualizar$', views.atualizar, name='atualizar'),
]