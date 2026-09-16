from django.urls import path
from .views import main_page, about, links, roulette, films, schedule, change_list

urlpatterns = [
    path('', main_page, name='main_page'),
    path('about/', about, name='about'),
    path('links/', links, name='links'),
    path('roulette/', roulette, name='roulette'),
    path('films/', films, name='films'),
    path('schedule/', schedule, name='schedule'),
    path('change_list/', change_list, name='change_list'),
]