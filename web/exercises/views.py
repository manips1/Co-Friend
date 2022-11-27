from django.http import JsonResponse
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
        # data from user
        data = json.loads(request.body)

        # compile the code
        compile_output = api.compile_code(data['source_code'])

        # response
        response_data = {
            'status':'ok',
            'stdout':'',
            'compile_output': compile_output,
            'time':'0',
            'memory':'0'
        }

        return JsonResponse(response_data)

    problem_dict = api.create_problem(['print'])
    context = {'problem': problem_dict['problem']}
    return render(request, 'exercises/editor.html', context)
