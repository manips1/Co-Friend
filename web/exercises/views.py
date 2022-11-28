from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from exercises.api import api
import json
import base64

# Create your views here.
# home
def home(request):
    # post
    if request.method == 'POST':
        keyword_list = request.POST.getlist('keyword_list')

        # generate a problem with keywords
        problem = api.create_problem_sentence(keyword_list)

        # encode the problem
        problem_b64 = base64.b64encode(problem.encode('ascii')).decode('ascii')
        return redirect('exercises:editor', problem_id=problem_b64)

    return render(request, 'exercises/home.html')


#editor
@ensure_csrf_cookie
def editor(request, problem_id):
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

    # decode problem
    problem = base64.b64decode(problem_id).decode('ascii')

    # generate example code and result
    ex_code = api.generate_code(problem)
    ex_result = api.compile_code(ex_code)

    context = {'problem': problem,'ex_result':ex_result}
    return render(request, 'exercises/editor.html', context)
