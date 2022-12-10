from django.urls import path
from exercises import views

app_name = 'exercises'

urlpatterns = [
    path('', views.home, name='home'),
    path('editor/', views.editor, name='editor'),
    path('share/', views.share, name='share'),
    path('test/', views.test_page, name='test')
]
