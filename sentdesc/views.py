from django.shortcuts import  get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views import generic
from django_pandas.io import read_frame
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Habilidades_Leitura, Atributos, Atributos_Habilidades, Elementos_Texto
from .forms import NameForm
import json

# Create your views here.

def index(request):
	ordered_sentdesc_list = Atributos_Habilidades.objects.select_related('habilidades')
	total_habilidades = Habilidades_Leitura.objects.all()
	total_atributos = Atributos.objects.all()
	
	context = {
		'ordered_sentdesc_list': ordered_sentdesc_list, 
		'total_habilidades': total_habilidades, 
		'total_atributos': total_atributos,
		}
	return render(request, 'sentdesc/index.html', context)

@login_required()
def detalhe(request, sent_desc_id):
	sent_desc = get_object_or_404(Habilidades_Leitura, pk=sent_desc_id)
	atributos = Atributos_Habilidades.objects.select_related('atributo').filter(habilidades=sent_desc_id)
	elementos_texto = Elementos_Texto.objects.all()
	link_filtro = ' '
	if request.GET.get('fonte_filtro') and request.GET.get('texto_filtro'):
		link_filtro = 'fonte_filtro=' + request.GET.get('fonte_filtro') + '&texto_filtro=' + request.GET.get('texto_filtro')
	if request.GET.get('page'):
		link_filtro = 'page=' + request.GET.get('page') + '&' + link_filtro
	context = {
		'sent_desc': sent_desc, 
		'atributos': atributos, 
		'elementos_texto': elementos_texto,
		'link_filtro': link_filtro,
	}
	return render(request, 'sentdesc/form_editar.html', context)

@login_required()	
def atualizar(request, sent_desc_id):
	if request.method == 'POST':
		habilidade = get_object_or_404(Habilidades_Leitura, pk=request.POST['sent_desc_id'])
		atributos = Atributos_Habilidades.objects.select_related('atributo').filter(habilidades=request.POST['sent_desc_id'])
		habilidade.sent_desc = request.POST['sent_desc']
		habilidade.save()
		context = {}
		for atributo in atributos:
			atributo.valor = request.POST['atributo' + str(atributo.id)]
			atributo.save()
			context[str(sent_desc_id) + '_atributo_' + str(atributo.id)] = request.POST['atributo' + str(atributo.id)]
		context['error_message'] = 'Habilidade de Leitura atualizada com sucesso'
		context['sent_desc_id'] = sent_desc_id
		context[str(sent_desc_id) + '_sent_desc'] = request.POST['sent_desc']
		print(context)
		return HttpResponse(
            json.dumps(context),
            content_type="application/json"
        )
		#return HttpResponseRedirect(reverse('sentdesc:index'))
		
def login(request):
    m = Member.objects.get(username=request.POST['username'])
    if m.password == request.POST['password']:
        request.session['member_id'] = m.id
        return HttpResponse(u"Você está autenticado.")
    else:
        return HttpResponse(u"Seu nome de usuário e senha não conferem.")
		