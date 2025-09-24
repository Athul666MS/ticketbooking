from django.shortcuts import render,redirect
from .models import Users

def index(request):

    return render(request,"index.html")

def register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")
        usr=Users()
        usr.name=name
        usr.email=email
        usr.password=password
        usr.role=role
        usr.save()



        return redirect("login")
    return render(request, "register.html")


def login(request):
    return render(request, "login.html")


def booking(request):

    return render(request,"booking.html")


def events(request):
    return render(request, "events.html")


def mybooking(request):
    return render(request, "mybookings.html")

def base(request):
    return render(request, "base.html")
