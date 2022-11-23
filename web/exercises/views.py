from django.shortcuts import render
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from exercises.api import api
import json

# Create your views here.
@ensure_csrf_cookie
def editor(request):
    # post
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data['source_code'])

    problem_dict = api.create_problem(['print'])
    context = {'problem': problem_dict['problem']}
    return render(request, 'exercises/editor.html', context)


