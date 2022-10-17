from django.urls import path
from exercises import views

urlpatterns = [
    path('', views.editor),
]
