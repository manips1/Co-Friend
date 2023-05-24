"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from allauth.account.views import confirm_email
from django.contrib.auth import logout
from django.shortcuts import redirect
from exercises.api.api import UserSolvedProblemlist

def logout_view(request):
    # 추가적인 로그아웃 전처리 작업이 있다면 여기에 추가

    logout(request)
    return redirect('/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('main.urls'), name='main'),
    path('exercises/', include('exercises.urls'), name='exercises'),
    path('logout/', logout_view, name='logout'),
    path('api/solved_list/', UserSolvedProblemlist.as_view(), name='problem_list'),
]
