from django.contrib import admin
from django.urls import path, include
from main import views
from allauth.account.views import confirm_email

urlpatterns = [
    path('', views.home),
    path('login/', views.login, name = 'login'),
]
