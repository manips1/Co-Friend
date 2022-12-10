from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.clickjacking import xframe_options_exempt
from exercises.api import api
import json
import base64

# Create your views here.
# home
def home(request):
    """exercises home page view

    Args:
        request (request): django request

    """
    # post
    if request.method == 'POST':
        keyword_list = request.POST.getlist('keyword_list')

        # generate a problem with keywords
        problem = api.create_problem_sentence(keyword_list)

        # encode the problem
        problem_b64 = base64.b64encode(problem.encode('ascii')).decode('ascii')
        return redirect(reverse('exercises:editor') + '?p=' + problem_b64)

    keywords = ['print', 'input', 'for', 'if', 'math']
    context = {'keywords': keywords}
    return render(request, 'exercises/home.html', context)


#editor
@ensure_csrf_cookie
def editor(request):
    """exercises editor page view

    Args:
        request (request): django request
        problem_id (string): base64 encoded problem

    """
    # post
    if request.method == 'POST':
        # data from user
        data = json.loads(request.body)

        # compile the code
        compile_output = api.compile_code(data['source_code'], data['stdin'])

        # response
        response_data = {
            'status':'ok',
            'stdout':'',
            'compile_output': compile_output,
            'time':'0',
            'memory':'0'
        }

        return JsonResponse(response_data)

    # get
    if request.method == 'GET':
        problem = request.GET.get('p', None)
        b64_p = problem

        # decode problem
        problem = base64.b64decode(problem).decode('ascii')

        # generate example code and result
        ex_code = api.generate_code(problem)
        ex_result = api.compile_code(ex_code, '1\r\n2\r\n3\r\n4')

        context = {'problem': problem, 'ex_result':ex_result, 'ex_code':ex_code, 'base64_problem': b64_p}
        return render(request, 'exercises/editor.html', context)


@xframe_options_exempt
def share(request):
    """exercises editor share page view

    Args:
        request (request): django request
        problem_id (string): base64 encoded problem

    """
    # post
    if request.method == 'POST':
        # data from user
        data = json.loads(request.body)

        # compile the code
        compile_output = api.compile_code(data['source_code'], data['stdin'])

        # response
        response_data = {
            'status':'ok',
            'stdout':'',
            'compile_output': compile_output,
            'time':'0',
            'memory':'0'
        }

        return JsonResponse(response_data)

    # get
    if request.method == 'GET':
        problem = request.GET.get('p', None)

        # decode problem
        problem = base64.b64decode(problem).decode('ascii')

        # generate example code and result
        ex_code = api.generate_code(problem)
        ex_result = api.compile_code(ex_code, '1\r\n2\r\n3\r\n4')

        context = {'problem': problem, 'ex_result':ex_result, 'ex_code':ex_code}
        return render(request, 'exercises/share_editor.html', context)


def test_page(request):
    return render(request, 'exercises/test_page.html')