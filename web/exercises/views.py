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
import requests
import matplotlib.pyplot as plt
import matplotlib
from requests.exceptions import RequestException
from django.contrib.auth.models import User
from .models import UserSolvedProblems

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
        b64_p = problem

        # decode problem
        problem = base64.b64decode(problem).decode('ascii')

        # generate example code and result
        ex_code = api.generate_code(problem)
        ex_result = api.compile_code(ex_code, '1\r\n2\r\n3\r\n4')

        context = {'problem': problem, 'ex_result': ex_result, 'ex_code': ex_code, 'base64_problem': b64_p}
        return render(request, 'exercises/share_editor.html', context)


@ensure_csrf_cookie
def grade(request):
    if request.method == 'POST':
        problem = request.POST.get('problem')
        user_code = request.POST.get('user-code')
        answer_code = request.POST.get('ex-code')
        grade_result = api.grade_code(problem, user_code, answer_code)
        username = request.user.username
        is_chat = request.POST.get('is-chat')
        keywords = request.POST.get('keywords').split(',')

        context = {'pass': grade_result['pass'], 'score': grade_result['score'], 'reason': grade_result['reason'],
                   'answer_code': answer_code, 'is_chat': is_chat, 'keywords': keywords}
        
                # UserSolvedProblems 모델 인스턴스 가져오기
        try:
            user_solved_problems = UserSolvedProblems.objects.get(user__username=username)
        except UserSolvedProblems.DoesNotExist:
            # 사용자에 대한 UserSolvedProblems 인스턴스가 없는 경우, 생성
            user = User.objects.get(username=username)
            user_solved_problems = UserSolvedProblems.objects.create(user=user)

        if grade_result['pass'] == True:
            # problems 필드 값 1 증가
            user_solved_problems.problems = str(int(user_solved_problems.problems) + 1)

            # solved 필드 값 1 증가
            user_solved_problems.solved += 1
            user_solved_problems.save()
        else:
            # problems 필드 값 1 증가
            user_solved_problems.problems = str(int(user_solved_problems.problems) + 1)
            user_solved_problems.save()
        return render(request, 'exercises/grade.html', context)


@csrf_exempt
def share_grade(request):
    if request.method == 'POST':
        problem = request.POST.get('problem')
        user_code = request.POST.get('user-code')
        answer_code = request.POST.get('ex-code')
        grade_result = api.grade_code(problem, user_code, answer_code)

        context = {'pass': grade_result['pass'], 'score': grade_result['score'], 'reason': grade_result['reason'],
                   'answer_code': answer_code}
        return render(request, 'exercises/share_grade.html', context)


def test_page(request):
    return render(request, 'exercises/test_page.html')


def about_us(request):
    return render(request, 'exercises/about_us.html')


def login(request):
    
    return render(request, 'exercises/login.html')

def mypage(request):
    matplotlib.use('Agg')
    # API에서 데이터 가져오기
    username = request.user.username
    print(username)
    url = 'http://127.0.0.1:8000/api/solved_list/'+ username+ '/'
    response = requests.get(url)
    data = response.json()
    print(data)
    # 데이터 가공
    if data:
        problems = int(data['problems'])  # 정수로 변환
        solved = int(data['solved'])  # 정수로 변환
        if problems == 0:
            success_rate = 0
        else:
            success_rate = solved / problems * 100  # 정답률 계산
    else:
        problems = 0
        solved = 0

    # 파이 차트 생성
    labels = ['Solved', 'Unsolved']
    sizes = [int(solved), int(problems) - int(solved)]
    colors = ['#E0708C', '#70B3E0']  # 멋진 색상으로 변경
    textprops = {'fontsize': 12, 'color': 'white', 'fontweight': 'bold'}  # 텍스트 스타일 변경
    explode = [0.05, 0]  # 조각 분리

    plt.figure(figsize=(8, 6))  # 차트의 크기 조정

    # 파이 차트
    plt.subplot(2, 2, 1)  # 그리드에 위치 설정
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90,
            explode=explode, textprops=textprops, shadow=True)  # 디자인 요소 적용
    plt.axis('equal')
    plt.title('Problem Status')


    # 차트 이미지를 저장
    chart_image_path = 'static/chart.png'
    plt.tight_layout()  # 차트 간격 조정
    plt.savefig(chart_image_path)

    # 템플릿에 전달할 context 설정
    context = {
        'chart_image_path': chart_image_path,
        'problems': problems,
        'solved': solved,
        'success_rate': success_rate,
    }
    
    return render(request, 'exercises/mypage.html', context)




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
