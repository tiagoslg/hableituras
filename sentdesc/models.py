from django.db import models
from django_pandas.managers import DataFrameManager

# Create your models here.
class Habilidades_Leitura(models.Model):
	id_origem = models.IntegerField(default=0)
	origem = models.CharField(max_length=200)
	sent_desc = models.TextField('Sentença Descritora')
	def __str__(self):
		return self.sent_desc
	
	objects = DataFrameManager()
	
class Atributos(models.Model):
	atributo = models.CharField(max_length=200)
	tipo = models.CharField(max_length=20)
	detalhamento = models.TextField()
	def __str__(self):
		return self.atributo
	
	objects = DataFrameManager()

class Atributos_Habilidades(models.Model):
	habilidades = models.ForeignKey(Habilidades_Leitura, on_delete=models.CASCADE)
	atributo = models.ForeignKey(Atributos, on_delete=models.CASCADE)
	valor = models.TextField()
	
	objects = DataFrameManager()