from django.db import models
from django_pandas.managers import DataFrameManager
from django.db.models.signals import post_save


# Create your models here.
class Habilidades_Leitura(models.Model):
	id_origem = models.IntegerField(default=0)
	origem = models.CharField(max_length=200)
	sent_desc = models.TextField('Sentença Descritora')
	def __str__(self):
		return self.sent_desc
	class Meta:
		verbose_name = ("Habilidade de Leitura")
		verbose_name_plural = ("Habilidades de Leitura")
	objects = DataFrameManager()
	
class Atributos(models.Model):
	TXT = 'TXT'
	NBR = 'NBR'
	LTXT = 'LTXT'
	DT = 'DT'
	TAB = 'TAB'
	TIPO_CHOICES = (
        (TXT, 'Texto'),
        (NBR, 'Número'),
        (LTXT, 'Texto Grande'),
        (DT, 'Data'),
		(TAB, 'Tabela Externa'),
	)
	atributo = models.CharField(max_length=200)
	tipo = models.CharField(
		max_length=4,
		choices=TIPO_CHOICES,
		default=TXT,
	)
	detalhamento = models.TextField()
	def __str__(self):
		return self.atributo
	class Meta:
		verbose_name = ("Atributo")
		verbose_name_plural = ("Atributos")
	objects = DataFrameManager()

class Atributos_Habilidades(models.Model):
	habilidades = models.ForeignKey(Habilidades_Leitura, on_delete=models.CASCADE)
	atributo = models.ForeignKey(Atributos, on_delete=models.CASCADE)
	valor = models.TextField()
	class Meta:
		verbose_name = ("Atributos / Habilidades")
		verbose_name_plural = ("Atributos / Habilidades")
	objects = DataFrameManager()
	
class Elementos_Texto(models.Model):
	categoria = models.IntegerField(default=0)
	elemento = models.CharField('Elementos do Texto', max_length=200, unique=True)
	def __str__(self):
		return self.elemento
	class Meta:
		verbose_name = ("Elemento do Texto")
		verbose_name_plural = ("Elementos do Texto")
	objects = DataFrameManager()

def atualizar_atributos_habilidades(sender, **kwargs):
	obj = kwargs['instance']
	print(obj.id)
	if kwargs['created']:
		if sender == Habilidades_Leitura:
			nova_habilidade = Habilidades_Leitura.objects.get(id=obj.id)
			total_atributos = Atributos.objects.all()
			for atributo_n in total_atributos:
				atributo_habilidade = Atributos_Habilidades(
					valor = '0',
				)
				atributo_habilidade.habilidades = nova_habilidade
				atributo_habilidade.atributo = atributo_n
				atributo_habilidade.save()
		else:
			total_habilidades = Habilidades_Leitura.objects.all()
			novo_atributo = Atributos.objects.get(id=obj.id)
			for habilidade_n in total_habilidades:
				atributo_habilidade = Atributos_Habilidades(
					valor = '0',
				)
				atributo_habilidade.habilidades = habilidade_n
				atributo_habilidade.atributo = novo_atributo
				atributo_habilidade.save()
		
	else:
		print("Registro atualizado")

post_save.connect(atualizar_atributos_habilidades, sender=Habilidades_Leitura)
post_save.connect(atualizar_atributos_habilidades, sender=Atributos)