from django.contrib import admin
from .models import Etiquetas, Textos, Dicionario, Sentencas

# Register your models here.
admin.site.register(Etiquetas)
admin.site.register(Textos)
admin.site.register(Dicionario)
admin.site.register(Sentencas)