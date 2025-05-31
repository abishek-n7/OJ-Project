from django.urls import path
from . import views

urlpatterns = [
    path('', views.contest_list, name='contest_list'),
    path('<int:contest_id>/problems/', views.contest_problem_list, name='contest_problem_list'),
    path('<int:contest_id>/problems/<int:problem_id>/', views.contest_problem_detail, name='contest_problem_detail'),
]
