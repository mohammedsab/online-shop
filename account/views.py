from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
# from django.contrib.auth.forms import l

from .forms import RegisterForm

# Create your views here.


def register(request):
    if request.user.is_authenticated:
        return redirect('shop:product_list')
    else:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request,user)
                return redirect('shop:product_list')
        else:
            form = RegisterForm()

        return render(request, 'account/registeration/register.html', {'form': form})

def user_login(request):
    pass
    # if request.method == 'POST':
    #     form = LoginForm(request.POST)
    #     if form.is_valid():
    #         cd = form.cleaned_data
    #         user = authenticate(request, username = cd['username'], password = cd['password'])
    #         if user is not None:
    #             login(request, user)
    #             return redirect('shop:product_list')

    return HttpResponse('login')

def user_logout(request):
    logout(request)
    return redirect('shop:product_list')



# docker build --tag python-django .
# docker run --publish 8000:8000 python-django