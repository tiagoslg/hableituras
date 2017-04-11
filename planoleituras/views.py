from django.shortcuts import  get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
import nltk, re
from pickle import load
from .models import Etiquetas, Textos, Dicionario, Sentencas

import json

# Create your views here.

def index(request):
	if request.POST:
		#processa o texto
		counts = {}
		counts['UNKN'] = 0
		tag_ignoradas = 0
		tag_list = {}
		totalProc = 0
		total_cow = 0
		total_ctw = 0
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
			print(texto_tagged)
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
							tag_ignoradas += 1
						if tag in tag_msentenca:
							t = 'PONT'
							tag_ignoradas += 1
						if t == 'Não Encontrado':
							t = 'UNKN'
							correto = False
						if t not in counts:
							counts[t] = 0 # does a exist in the current namespace
						counts[t] += 1
						if t != 'UNKN':
							totalProc += 1
						etiqueta_f = etiquetas.filter(etiqueta=t)
						dicionario = Dicionario(etiqueta = etiqueta_f[0], texto = texto_bd, palavra = word, correto = correto)
						dicionario.save()
						itens_sentencas.append(dicionario.id)
						if etiqueta_f[0].tipo_etiqueta == 'MSE':
							sentencas[sentenca] = itens_sentencas
							itens_sentencas= []
							sentenca += 1
						if etiqueta_f[0].tipo_etiqueta != 'IGN':
							if t not in tag_list:
								tag_list[t] = etiqueta_f[0].descritor
							if etiqueta_f[0].tipo_etiqueta == 'COW':
								total_cow += 1
							if etiqueta_f[0].tipo_etiqueta == 'CTW':
								total_ctw += 1
						texto_etiquetado[dicionario.id] = {'id_tag':dicionario.id, 
							'word':word, 
							'tag':etiqueta_f[0].etiqueta, 
							'tag_desc':etiqueta_f[0].descritor,
							'tipo_etiqueta':etiqueta_f[0].tipo_etiqueta}
			total = len(texto_tagged)
			estatisticas_sentencas = gravar_sentencas(texto_id, sentencas)
		else:
			texto_id = texto_bd.id
			dicionario = Dicionario.objects.select_related('etiqueta').filter(texto=texto_id).order_by('id')
			total = dicionario.count()
			estatisticas_sentencas = get_estatisticas_sentenca(texto_id)
			for item in dicionario:
				texto_etiquetado[item.id] = {'id_tag':item.id, 
					'word':item.palavra, 
					'tag':item.etiqueta.etiqueta,
					'tag_desc':item.etiqueta.descritor,
					'tipo_etiqueta':item.etiqueta.tipo_etiqueta}
				if texto_etiquetado[item.id]['tag'] == 'PONT':
					tag_ignoradas += 1
					totalProc += 1
				else:
					if texto_etiquetado[item.id]['tag'] not in counts:
						counts[texto_etiquetado[item.id]['tag']] = 0 # does a exist in the current namespace
					counts[texto_etiquetado[item.id]['tag']] += 1
					if texto_etiquetado[item.id]['tag'] != 'UNKN':
						totalProc += 1
					if texto_etiquetado[item.id]['tipo_etiqueta'] != 'IGN':
						if texto_etiquetado[item.id]['tag'] not in tag_list:
							tag_list[texto_etiquetado[item.id]['tag']] = texto_etiquetado[item.id]['tag_desc']
						if texto_etiquetado[item.id]['tipo_etiqueta'] == 'COW':
							total_cow += 1
						if texto_etiquetado[item.id]['tipo_etiqueta'] == 'CTW':
							total_ctw += 1
		totalNProc = counts.pop('UNKN', 0)
		counts = list(sorted(counts.items()))
		print(estatisticas_sentencas)
		context = {'error_message': 'Processando o Texto', 
			'titulo': titulo,
			'counts': dict(counts),
			'total': total,
			'totalProc': totalProc,
			'totalNProc': totalNProc,
			'total_cow': total_cow,
			'total_ctw': total_ctw,
			'tag_ignoradas': tag_ignoradas,
			'tag_list': tag_list,
			'etiquetas': get_etiquetas(),
			'texto_etiquetado': texto_etiquetado,
			'texto_id': texto_id,
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
				dicionario = Dicionario.objects.select_related('etiqueta').filter(palavra=palavra).order_by('id')
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
		context['tag_id'] = tag_id
		context['todas'] = todas
		context['tag_nova'] = tag_nova
		context['tag_atual'] = tag_atual
		context['tag_id_alterado'] = list_id
		context['total'] = estatisticas['total']
		context['totalProc'] = estatisticas['totalProc']
		context['tag_ignoradas'] = estatisticas['tag_ignoradas']
		context['total_ctw'] = estatisticas['total_ctw']
		context['total_cow'] = estatisticas['total_cow']
		context['totalNProc'] = estatisticas['totalNProc']
		
		return HttpResponse(
			json.dumps(context),
			content_type="application/json"
		)
		#return HttpResponseRedirect(reverse('sentdesc:index'))

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

def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None

def get_estatisticas_texto(texto_id):
	texto = get_object_or_404(Textos, pk=texto_id)
	dicionario = Dicionario.objects.select_related('etiqueta').filter(texto=texto_id).order_by('id')
	estatisticas = {}
	estatisticas['total'] = str(len(dicionario))
	filtro = dicionario.exclude(etiqueta__etiqueta='UNKN')
	estatisticas['totalProc'] = str(len(filtro))
	filtro = dicionario.filter(etiqueta__etiqueta='PONT').filter(etiqueta__etiqueta='MSE')
	estatisticas['tag_ignoradas'] = str(len(filtro))
	filtro = dicionario.filter(etiqueta__tipo_etiqueta='CTW')
	estatisticas['total_ctw'] = str(len(filtro))
	filtro = dicionario.filter(etiqueta__tipo_etiqueta='COW')
	estatisticas['total_cow'] = str(len(filtro))
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
		estatisticas[sentenca.ordem]['total_ctw'] = str(len(filtro))
		filtro = dicionario.filter(etiqueta__tipo_etiqueta='COW')
		estatisticas[sentenca.ordem]['total_cow'] = str(len(filtro))
		estatisticas[sentenca.ordem]['itens'] = []
		for item in dicionario:
			estatisticas[sentenca.ordem]['itens'].append(item.palavra)
		
	return estatisticas
