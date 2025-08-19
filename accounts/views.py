from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect("payroll:dashboard")
    


    if request.method == "POST":
        username = request.POST.get("username").strip().lower()
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("payroll:dashboard")
        else:
            messages.error(request, "Invalid username or password")
    context = {'page': page}
    return render(request, "accounts/login.html", context)

@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")
