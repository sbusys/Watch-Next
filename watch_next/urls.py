from django.urls import path
from . import views

app_name = 'watch_next'

urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('None', views.trailer, name='trailer')
]
