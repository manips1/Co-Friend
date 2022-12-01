from django.shortcuts import render

# Create your views here.


def home(request):
    """main home page view

    Args:
        request (request): django request

    """
    return render(request, 'main/home.html')
