from django.conf.urls import url

from . import views

app_name = 'sentdesc'
urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^(?P<sent_desc_id>[0-9]+)/$', views.detalhe, name='detalhe'),
	url(r'^(?P<sent_desc_id>[0-9]+)/atualizar$', views.atualizar, name='atualizar'),
	url(r'^login/', views.login, name='login'),
]