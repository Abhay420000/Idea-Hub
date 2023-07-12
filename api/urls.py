from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("<int:year>/", views.Year_Wise.as_view()),
    path("<int:year>/<int:month>/", views.Year_Month_Wise.as_view()),
    path("<int:year>/<int:month>/<int:day>/", views.Year_Month_Day_Wise.as_view()),
    path("<str:pid>/", views.PostAndComments.as_view()),
    path("<str:pid>/comment/", views.Comment.as_view()),
    path("<str:pid>/rate/", views.Rate.as_view()),
    path("<str:pid>/<str:cid>/edit/", views.EditComment.as_view()),
    path("", views.Posts.as_view()),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]