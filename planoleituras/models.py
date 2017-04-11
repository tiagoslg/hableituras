from django.db import models

# Create your models here.
class Etiquetas(models.Model):
	etiqueta = models.CharField(max_length=20, unique=True)
	descritor = models.CharField(max_length=100)
	CTW = 'CTW'
	COW = 'COW'
	IGN = 'IGN'
	MSE = 'MSE'
	TIPO_CHOICES = (
        (CTW, 'Palavras de Conteúdo'),
        (COW, 'Palavras Comuns'),
		(MSE, 'Marcador de Sentença'),
		(IGN, 'Ignoradas'),
	)
	tipo_etiqueta = models.CharField(
		max_length=4,
		choices=TIPO_CHOICES,
		default=COW,
	)
	def __str__(self):
		return self.etiqueta + ' - ' + self.descritor
	class Meta:
		verbose_name = ("Etiqueta")
		verbose_name_plural = ("Etiquetas")
		
class Textos(models.Model):
	titulo = models.CharField(max_length=250)
	texto = models.TextField('Texto completo')
	origem = models.CharField(max_length=100)
	def __str__(self):
		return self.titulo + '(' + self.origem + ')'
	class Meta:
		verbose_name = ("Texto")
		verbose_name_plural = ("Textos")

class Dicionario(models.Model):
	etiqueta = models.ForeignKey(Etiquetas, 
		on_delete = models.SET_NULL,
		blank=True,
		null=True,
	)
	texto = models.ForeignKey(Textos, 
		on_delete = models.CASCADE
	) 
	palavra = models.CharField(max_length=50)
	correto = models.BooleanField(default=True)
	def __str__(self):
		return self.palavra #+ '(' + self.etiqueta + ')'
	class Meta:
		verbose_name = ("Palavra Etiqueta")
		verbose_name_plural = ("Palavras Etiquetadas")

class Sentencas(models.Model):
	texto = models.ForeignKey(Textos, 
		on_delete = models.CASCADE
	) 
	ordem = models.IntegerField(default=0)
	itens = models.CharField(
		max_length=250,
	)
	class Meta:
		verbose_name = ("Sentença")
		verbose_name_plural = ("Sentenças")