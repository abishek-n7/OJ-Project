from django.urls import path
from problems.views import problem_list, problem_detail
from . import views

urlpatterns = [
    path('', problem_list, name='problem_list'),
    path('problems/<int:problem_id>/', problem_detail, name='problem_detail'),
    path('problem/<int:problem_id>/save/', views.save_problem, name='save_problem'),
]