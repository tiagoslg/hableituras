from django import forms

class NameForm(forms.Form):
	fonte_filtro = forms.ChoiceField(choices=('origem', 'sentenca_descritora'))
	texto_filtro = forms.CharField(label='Valor', max_length=100)