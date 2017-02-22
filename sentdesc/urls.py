from django.conf.urls import url

from . import views

app_name = 'sentdesc'
urlpatterns = [
	url(r'^$', views.index, name='index'),
	#url(r'^(?P<sent_desc_id>[0-9]+)/(?P<link_filtro>\S+)$', views.detalhe, name='detalhe'),
	url(r'^(?P<sent_desc_id>[0-9]+)/$', views.detalhe, name='detalhe'),
	url(r'^(?P<sent_desc_id>[0-9]+)/atualizar$', views.atualizar, name='atualizar'),
	url(r'^login/', views.login, name='login'),
]
#app_name = 'polls'
#urlpatterns = [
#    url(r'^$', views.IndexView.as_view(), name='index'),
	# ex: /polls/5/
#    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    # ex: /polls/5/results/
#    url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    # ex: /polls/5/vote/
#    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
#]