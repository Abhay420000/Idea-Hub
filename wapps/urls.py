from django.urls import path
from . import views

urlpatterns = [
    path('create', views.Create.as_view()),
    path('', views.Home.as_view()),
    path('login', views.Login.as_view()),
    path('signup', views.Sign_Up.as_view()),
    path('user_profile', views.User_Profile.as_view()),
]
