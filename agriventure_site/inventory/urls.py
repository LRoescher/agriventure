from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('newentry/', views.newentry, name='newentry'),
    path('list/', views.list, name='list')
]