from django.shortcuts import  get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django_pandas.io import read_frame
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Habilidades_Leitura, Atributos, Atributos_Habilidades
from .forms import NameForm

# Create your views here.

def index(request):
	if request.user.is_authenticated():
		print('Autenticado')
	else:
		print('Não Autenticado')
	if request.GET.get('fonte_filtro') and request.GET.get('texto_filtro'):
		link_filtro = 'fonte_filtro=' + request.GET.get('fonte_filtro') + '&texto_filtro=' + request.GET.get('texto_filtro')
		if request.GET.get('fonte_filtro') == 'origem':
			ordered_sentdesc_list = Atributos_Habilidades.objects.select_related('habilidades').filter(habilidades__origem__icontains=request.GET.get('texto_filtro'))
			total_habilidades = Habilidades_Leitura.objects.all().filter(origem__icontains=request.GET.get('texto_filtro'))
		elif request.GET.get('fonte_filtro') == 'sentenca_descritora':
			ordered_sentdesc_list = Atributos_Habilidades.objects.select_related('habilidades').filter(habilidades__sent_desc__icontains=request.GET.get('texto_filtro'))
			total_habilidades = Habilidades_Leitura.objects.all().filter(sent_desc__icontains=request.GET.get('texto_filtro'))
		else:
			ordered_sentdesc_list = list(Atributos_Habilidades.objects.all().filter(atributo=request.GET.get('fonte_filtro'), valor=request.GET.get('texto_filtro')))
			list_hab_id = [ item_list.habilidades.id for item_list in ordered_sentdesc_list]
			ordered_sentdesc_list = Atributos_Habilidades.objects.select_related('habilidades').filter(habilidades__id__in=list_hab_id)
			total_habilidades = Habilidades_Leitura.objects.all().filter(id__in=list_hab_id)
		print(ordered_sentdesc_list)
		total_atributos = Atributos.objects.all()
		
	else:
		ordered_sentdesc_list = Atributos_Habilidades.objects.select_related('habilidades')
		total_habilidades = Habilidades_Leitura.objects.all()
		total_atributos = Atributos.objects.all()
		link_filtro = ''
	
	page = request.GET.get('page', 1)
	paginator = Paginator(total_habilidades, 50)
	try:
		total_habilidades = paginator.page(page)
	except PageNotAnInteger:
		total_habilidades = paginator.page(1)
	except EmptyPage:
		total_habilidades = paginator.page(paginator.num_pages)
	context = {
		'ordered_sentdesc_list': ordered_sentdesc_list, 
		'total_habilidades': total_habilidades, 
		'total_atributos': total_atributos,
		'link_filtro': link_filtro,
		}
	return render(request, 'sentdesc/index.html', context)

@login_required()
def detalhe(request, sent_desc_id):
	sent_desc = get_object_or_404(Habilidades_Leitura, pk=sent_desc_id)
	atributos = Atributos_Habilidades.objects.select_related('atributo').filter(habilidades=sent_desc_id)
	context = {'sent_desc': sent_desc, 'atributos': atributos}
	return render(request, 'sentdesc/form_editar.html', context)

@login_required()	
def atualizar(request, sent_desc_id):
	if request.method == 'POST':
		habilidade = get_object_or_404(Habilidades_Leitura, pk=request.POST['sent_desc_id'])
		atributos = Atributos_Habilidades.objects.select_related('atributo').filter(habilidades=request.POST['sent_desc_id'])
		habilidade.sent_desc = request.POST['sent_desc']
		habilidade.origem = request.POST['origem']
		habilidade.id_origem = request.POST['id_origem']
		habilidade.save()
		for atributo in atributos:
			atributo.valor = request.POST['atributo' + str(atributo.id)]
			atributo.save()
		context = {'error_message': 'Habilidade de Leitura atualizada com sucesso',}
		error_message = 'Habilidade de Leitura atualizada com sucesso'
		return HttpResponseRedirect(reverse('sentdesc:index'))
		
def login(request):
    m = Member.objects.get(username=request.POST['username'])
    if m.password == request.POST['password']:
        request.session['member_id'] = m.id
        return HttpResponse(u"Você está autenticado.")
    else:
        return HttpResponse(u"Seu nome de usuário e senha não conferem.")