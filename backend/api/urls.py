from django.shortcuts import render
from django.urls import path
from .views import welcome

urlpatterns = [
    path('welcome/', welcome),
]

