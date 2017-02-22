from django.contrib import admin

from .models import Habilidades_Leitura, Atributos, Elementos_Texto

# Register your models here.

admin.site.register(Habilidades_Leitura)
admin.site.register(Atributos)
admin.site.register(Elementos_Texto)