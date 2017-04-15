from django.shortcuts import render

# Create your views here.
def index(request):
    context_dict = None
    return render(request, 'core/index.html', context_dict)