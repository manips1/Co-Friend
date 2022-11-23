from django.shortcuts import render
from exercises.api import api

# Create your views here.


def editor(request):
    problem_dict = api.create_problem(['print'])
    context = {'problem': problem_dict['problem']}
    return render(request, 'exercises/editor.html', context)
