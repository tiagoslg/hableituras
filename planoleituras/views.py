from django.shortcuts import  get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
import nltk, re
from pickle import load
from .models import Etiquetas, Textos, Dicionario, Sentencas
from django.db.models import Count

import json

# Create your views here.

def index(request):
	if request.POST:
		#processa o texto
		texto_etiquetado = {}
		etiquetas = Etiquetas.objects.all().order_by('etiqueta')
		texto = request.POST['texto']
		titulo = request.POST['titulo']
		origem = request.POST['origem']
		if origem == '':
			origem = 'Não definido'
		texto_bd = get_or_none(Textos, texto=texto)
		if not texto_bd:
			texto_bd = Textos(titulo = titulo, texto = texto, origem = origem)
			texto_bd.save()
			texto_id = texto_bd.id
			input = open('C:\\Users\\Tiago Gomes\\projects\\hableituras\\planoleituras\\t3_cut2.pkl', 'rb')
			tagger = load(input)
			input.close()
			texto = remover_caracteres_especiais(texto)
			tokens = nltk.word_tokenize(texto)
			texto_tagged = tagger.tag(tokens)
			tag_ignore = [',',':']
			tag_msentenca = ['.','!','?','...']
			sentenca = 1
			sentencas = {}
			itens_sentencas = []
			for word,tag in texto_tagged:
				tags = tag.split('|')
				correto = True
				for t in tags:
					if t != '+':
						if t in tag_ignore:
							t = 'IGN'
						if tag in tag_msentenca:
							t = 'PONT'
						if t == 'Não Encontrado':
							t = 'UNKN'
							palavra_existe = Dicionario.objects.select_related('etiqueta').filter(palavra=word).exclude(etiqueta__etiqueta='UNKN')
							if len(palavra_existe) > 0:
								t = palavra_existe[0].etiqueta.etiqueta
						etiqueta_f = etiquetas.filter(etiqueta=t)
						dicionario = Dicionario(etiqueta = etiqueta_f[0], texto = texto_bd, palavra = word, correto = correto)
						dicionario.save()
						itens_sentencas.append(dicionario.id)
						if etiqueta_f[0].tipo_etiqueta == 'MSE':
							sentencas[sentenca] = itens_sentencas
							itens_sentencas= []
							sentenca += 1
						texto_etiquetado[dicionario.id] = {'id_tag':dicionario.id, 
							'word':word, 
							'tag':etiqueta_f[0].etiqueta, 
							'tag_desc':etiqueta_f[0].descritor,
							'tipo_etiqueta':etiqueta_f[0].tipo_etiqueta}
			estatisticas_sentencas = gravar_sentencas(texto_id, sentencas)
		else:
			texto_id = texto_bd.id
			dicionario = Dicionario.objects.select_related('etiqueta').filter(texto=texto_id).order_by('id')
			for item in dicionario:
				if item.etiqueta.etiqueta == 'UNKN':
					palavra_existe = Dicionario.objects.select_related('etiqueta').filter(palavra=item.palavra).exclude(etiqueta__etiqueta='UNKN')
					if len(palavra_existe) > 0:
						t = palavra_existe[0].etiqueta
						item.etiqueta = t
						item.save()
				texto_etiquetado[item.id] = {'id_tag':item.id, 
					'word':item.palavra, 
					'tag':item.etiqueta.etiqueta,
					'tag_desc':item.etiqueta.descritor,
					'tipo_etiqueta':item.etiqueta.tipo_etiqueta}
			estatisticas_sentencas = get_estatisticas_sentenca(texto_id)
		print(estatisticas_sentencas)
		tag_list_c = get_tag_list(texto_id)
		estatisticas_texto = get_estatisticas_texto(texto_id)
		context = {'error_message': 'Texto Processado com Sucesso', #mensagem de conclusão do processo 
			'titulo': titulo, #Título do texto
			'total': estatisticas_texto['total'], #total de itens analisados
			'totalProc': estatisticas_texto['totalProc'], #total de itens taggeados
			'totalNProc': estatisticas_texto['totalNProc'], #total de itens ignorados
			'totalPCo': estatisticas_texto['totalPCo'], #total de palavras comuns
			'totalPCt': estatisticas_texto['totalPCt'], #total de palavras de conteúdo
			'totalIgn': estatisticas_texto['totalIgn'], #total de itens ignorados
			'etiquetas': get_etiquetas(), #lista de etiquetas (tags) para o select de edição
			'texto_etiquetado': texto_etiquetado, #texto completo com as tags
			'texto_id': texto_id, #id do texto analisado, após gravação no BD
			'tag_list_c': tag_list_c, #lista de tags e totais por tag para o dicionario de tags
			'estatisticas_sentencas': estatisticas_sentencas, #estatisticas gerais das sentenças que compõem o texto
		}
	else:
		#mostra o form normal
		context = {'error_message': 'Insira o texto a ser processado',}
	
	return render(request, 'planoleituras/index.html', context)

def detalhe(request, tag_id):
	#sent_desc = get_object_or_404(Habilidades_Leitura, pk=sent_desc_id)
	#atributos = Atributos_Habilidades.objects.select_related('atributo').filter(habilidades=sent_desc_id)
	#elementos_texto = Elementos_Texto.objects.all()
	context = {
		'etiquetas': get_etiquetas(),
		'tag_id': tag_id,
		'tag_atual': 'PROPESS',
	}
	return render(request, 'planoleituras/form_editar.html', context)

def atualizar(request, tag_id):
	if request.method == 'POST':
		tag_atual = request.POST['tag_atual']
		tag_nova = request.POST['tag_nova']
		todas = request.POST['todas']
		texto_id = request.POST['texto_id']
		context = {}
		if tag_atual != tag_nova:
			dicionario = get_object_or_404(Dicionario, pk=tag_id)
			palavra = dicionario.palavra
			list_id = ''
			etiqueta = get_object_or_404(Etiquetas, etiqueta=tag_nova)
			if todas == '1':
				dicionario = Dicionario.objects.select_related('etiqueta').filter(palavra=palavra).filter(texto=texto_id).order_by('id')
				for item in dicionario:
					item.etiqueta = etiqueta
					item.correto = False
					list_id = list_id + str(item.id) + '|'
					item.save()
			else:
				dicionario = get_object_or_404(Dicionario, pk=tag_id)
				dicionario.etiqueta = etiqueta
				dicionario.correto = False
				list_id = str(dicionario.id)
				dicionario.save()
			context['error_message'] = 'Item atualizado com sucesso'
		else:
			list_id = tag_id
			context['error_message'] = 'Item não alterado'
		estatisticas = get_estatisticas_texto(texto_id)
		estatisticas_sentencas = get_estatisticas_sentenca(texto_id)
		tag_list_c = get_tag_list(texto_id)
		context['tag_id'] = tag_id
		context['todas'] = todas
		context['tag_nova'] = tag_nova
		context['tag_atual'] = tag_atual
		context['tag_id_alterado'] = list_id
		context['total'] = estatisticas['total']
		context['totalProc'] = estatisticas['totalProc']
		context['totalIgn'] = estatisticas['totalIgn']
		context['totalPCt'] = estatisticas['totalPCt']
		context['totalPCo'] = estatisticas['totalPCo']
		context['totalNProc'] = estatisticas['totalNProc']
		context['tag_list_c'] = {}
		x = 0
		for descritor in sorted(tag_list_c):
			context['tag_list_c'][x] = str(tag_list_c[descritor]['etiqueta']) + ' - ' + str(tag_list_c[descritor]['descritor']) + ' (' + str(tag_list_c[descritor]['total']) + ') '
			x += 1
		context['estatisticas_sentencas'] = {}
		for item in sorted(estatisticas_sentencas):
			context['estatisticas_sentencas']['total_sent_'+str(item)] = str(estatisticas_sentencas[item]['total'])
			context['estatisticas_sentencas']['totalPCo_sent_'+str(item)] = str(estatisticas_sentencas[item]['totalPCo'])
			context['estatisticas_sentencas']['totalPCt_sent_'+str(item)] = str(estatisticas_sentencas[item]['totalPCt'])
		return HttpResponse(
			json.dumps(context),
			content_type="application/json"
		)

def get_etiquetas():
	etiquetas = Etiquetas.objects.all()
	context = {}
	for etiqueta in etiquetas:
		context[etiqueta.etiqueta] = etiqueta.descritor
	return context

def remover_caracteres_especiais(text):
	if isinstance(text, str):
		text = re.sub('\"', '', text)
		#text = re.sub('\n', '.\n', text)
		#text = text.replace('....','...')
		#text = text.replace('..','.')
		#text = text.replace('!.','!')
		#text = text.replace('?.','?')
		return text

def select_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None

def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None

def get_tag_list(texto_id):
	dicionario = Dicionario.objects.all().values('etiqueta__etiqueta', 'etiqueta__descritor').annotate(total=Count('palavra')).filter(texto=texto_id).exclude(etiqueta__etiqueta='UNKN').exclude(etiqueta__etiqueta='IGN').order_by('etiqueta__descritor')
	tag_list = {}
	for item in dicionario:
		tag_list[item['etiqueta__descritor']] = {}
		tag_list[item['etiqueta__descritor']]['etiqueta'] = item['etiqueta__etiqueta']
		tag_list[item['etiqueta__descritor']]['descritor'] = item['etiqueta__descritor']
		tag_list[item['etiqueta__descritor']]['total'] = item['total']
	return tag_list

def get_estatisticas_texto(texto_id):
	#texto = get_object_or_404(Textos, pk=texto_id)
	dicionario = Dicionario.objects.select_related('etiqueta').filter(texto=texto_id).order_by('id')
	estatisticas = {}
	estatisticas['total'] = str(len(dicionario))
	filtro = dicionario.exclude(etiqueta__etiqueta='UNKN')
	estatisticas['totalProc'] = str(len(filtro))
	filtro = dicionario.filter(etiqueta__tipo_etiqueta='IGN').exclude(etiqueta__etiqueta='UNKN')
	estatisticas['totalIgn'] = str(len(filtro))
	filtro = dicionario.filter(etiqueta__tipo_etiqueta='CTW')
	estatisticas['totalPCt'] = str(len(filtro))
	filtro = dicionario.filter(etiqueta__tipo_etiqueta='COW')
	estatisticas['totalPCo'] = str(len(filtro))
	totalNProc = str(int(estatisticas['total']) - int(estatisticas['totalProc']))
	estatisticas['totalNProc'] = totalNProc
	return estatisticas

def gravar_sentencas(texto_id, sentencas):
	texto = get_object_or_404(Textos, pk=texto_id)
	for x,y in sentencas.items():
		itens = str(y)
		itens = str(y).strip('[]')
		sentenca = Sentencas(texto = texto, ordem = x, itens = itens)
		sentenca.save()
	
	estatisticas_sentencas = get_estatisticas_sentenca(texto_id)
	return estatisticas_sentencas

def get_estatisticas_sentenca(texto_id):
	texto = get_object_or_404(Textos, pk=texto_id)
	sentencas = Sentencas.objects.select_related('texto').filter(texto=texto_id).order_by('ordem')
	estatisticas = {}
	for sentenca in sentencas:
		itens = sentenca.itens.split(', ')
		itens_int = []
		for i in itens: 
			itens_int.append(int(i))
		print()
		dicionario = Dicionario.objects.select_related('etiqueta').filter(id__in=itens_int).order_by('id')
		estatisticas[sentenca.ordem] = {}
		estatisticas[sentenca.ordem]['total'] = str(len(dicionario))
		filtro = dicionario.filter(etiqueta__tipo_etiqueta='CTW')
		estatisticas[sentenca.ordem]['totalPCt'] = str(len(filtro))
		filtro = dicionario.filter(etiqueta__tipo_etiqueta='COW')
		estatisticas[sentenca.ordem]['totalPCo'] = str(len(filtro))
		estatisticas[sentenca.ordem]['itens'] = []
		for item in dicionario:
			estatisticas[sentenca.ordem]['itens'].append(item.palavra)
		
	return estatisticas
