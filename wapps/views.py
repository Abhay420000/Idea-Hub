from django.shortcuts import render
from django.views import View

class Create(View):    
    def get(self, request):
        return render(request, 'wapps/create.html')

class Home(View):
    def get(self, request):
        return render(request, 'wapps/home.html')

class User_Profile(View):
    def get(self, request):
        return render(request, 'wapps/user_profile.html')

class Login(View):
    def get(self, request):
        return render(request, 'wapps/login.html')

class Sign_Up(View):
    def get(self, request):
        return render(request, 'wapps/signup.html')