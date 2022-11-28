from django.urls import path
from exercises import views

app_name = 'exercises'

urlpatterns = [
    path('', views.home, name='home'),
    path('editor/<str:problem_id>/', views.editor, name='editor'),
]
