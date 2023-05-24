from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from exercises.api import api
import json
import base64
from rest_framework import generics
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount

# Create your views here.
# home
def home(request):
    if request.method == 'POST':
        keyword_list = ['print', 'input', 'for', 'if', 'math']

        # generate a problem with keywords
        problem = api.create_problem_sentence(keyword_list, False)

        # encode the problem
        problem_b64 = base64.b64encode(problem.encode('ascii')).decode('ascii')
        return redirect(reverse('exercises:editor') + '?p=' + problem_b64 + '&chat=false')

    return render(request, 'exercises/home.html')


#problem type
def problem_type(request):
    """exercises home page view

        Args:
            request (request): django request

        """
    # post
    if request.method == 'POST':
        keyword_list = request.POST.getlist('keyword_list')

        # generate a problem with keywords
        problem = api.create_problem_sentence(keyword_list, True)

        # encode the problem
        problem_b64 = base64.b64encode(problem.encode('ascii')).decode('ascii')
        keywords = ''
        for keyword in keyword_list:
            keywords += '&keyword=' + keyword
        return redirect(reverse('exercises:editor') + '?p=' + problem_b64 + '&chat=true' + keywords)

    return render(request, 'exercises/problem_type.html')


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

        if data['type'] == 'run':

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

        is_chat = request.GET.get('chat')
        keywords = ''
        if is_chat:
            keyword_list = request.GET.getlist('keyword')
            for keyword in keyword_list:
                keywords += keyword + ','

        # generate example code and result
        ex_code = api.generate_code(problem)
        ex_result = api.compile_code(ex_code, '1\r\n2\r\n3\r\n4')

        context = {'problem': problem, 'ex_result': ex_result, 'ex_code': ex_code, 'base64_problem': b64_p,
                   'is_chat': is_chat, 'keywords': keywords[:-1]}
        return render(request, 'exercises/editor.html', context)


@csrf_exempt
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


@ensure_csrf_cookie
def grade(request):
    if request.method == 'POST':
        problem = request.POST.get('problem')
        user_code = request.POST.get('user-code')
        answer_code = request.POST.get('ex-code')
        grade_result = api.grade_code(problem, user_code, answer_code)

        is_chat = request.POST.get('is-chat')
        keywords = request.POST.get('keywords').split(',')

        context = {'pass': grade_result['pass'], 'score': grade_result['score'], 'reason': grade_result['reason'],
                   'answer_code': answer_code, 'is_chat': is_chat, 'keywords': keywords}
        return render(request, 'exercises/grade.html', context)


def test_page(request):
    return render(request, 'exercises/test_page.html')

def about_us(request):
    return render(request, 'exercises/about_us.html')


def login(request):
    
    return render(request, 'exercises/login.html')


class my_social:
    def get_current_user_uid(request):
        if request.user.is_authenticated:
            try:
                social_account = SocialAccount.objects.get(user=request.user)
                uid = social_account.uid
                return uid
            except SocialAccount.DoesNotExist:
                pass
        return None
