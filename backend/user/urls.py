from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.profiles_list, name='users'),
    path('user/<str:pk>/', views.profile, name='user')
]
