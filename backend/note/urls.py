from django.urls import path
from . import views

urlpatterns = [
    path('notes/', views.notes_list, name='notes'),
    path('note/<str:pk>', views.note, name='note'),
    path('tags/', views.tags_list, name='tags'),
    path('tag/<str:pk>', views.tag, name='tag'),
]
