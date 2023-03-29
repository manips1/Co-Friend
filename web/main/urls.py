from django.contrib import admin
from django.urls import path, include
from main import views

urlpatterns = [
    path('', views.home),
    path('login/', views.login, name = 'login'),
    
]
