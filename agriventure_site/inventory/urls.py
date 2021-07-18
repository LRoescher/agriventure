from django.urls import path

from . import views
from .views import InventoryListView

urlpatterns = [
    path('', views.index, name='index'),
    path('newentry/', views.newentry, name='newentry'),
    path('list/', InventoryListView.as_view(), name='list')
]