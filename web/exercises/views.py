from django.shortcuts import render

# Create your views here.


def editor(request):
    return render(request, 'exercises/editor.html')
