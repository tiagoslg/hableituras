from django.shortcuts import render
import nltk
from pickle import load

# Create your views here.

def index(request):
	if request.POST:
		#processa o texto
		input = open('C:\\Users\\Tiago Gomes\\projects\\hableituras\\planoleituras\\t2.pkl', 'rb')
		tagger = load(input)
		texto = request.POST['texto']
		texto = texto.lower()
		input.close()
		tokens = nltk.word_tokenize(texto)
		texto_tagged = tagger.tag(tokens)
		counts = {}
		totalProc = 0
		for w,t in texto_tagged:
			if t not in counts:
				counts[t] = 0 # does a exist in the current namespace
			counts[t] += 1
			if t != 'NoEsp':
				totalProc += 1
		
		total = len(texto_tagged)
		counts = list(sorted(counts.items()))
		context = {'error_message': 'Processando o Texto', 
			'texto_tagged': texto_tagged,
			'counts': counts,
			'total': total,
			'totalProc': totalProc,}
	else:
		#mostra o form normal
		context = {'error_message': 'Insira o texto a ser processado',}
	
	return render(request, 'planoleituras/index.html', context)
