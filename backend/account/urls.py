from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('reset-password/', views.request_password_reset, name="reset_password"),
    path('reset-password/<str:uidb64>/<str:token>/',
         views.reset_password, name="reset_password")
]
