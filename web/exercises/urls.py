from django.urls import path
from exercises import views

app_name = 'exercises'

urlpatterns = [
    path('', views.home, name='home'),
    path('problem_type/', views.problem_type, name='problem_type'),
    path('editor/', views.editor, name='editor'),
    path('share/', views.share, name='share'),
    path('grade/', views.grade, name='grade'),
    path('test/', views.test_page, name='test')
]
