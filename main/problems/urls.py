from django.urls import path
from problems.views import problem_list, problem_detail

urlpatterns = [
    path('', problem_list, name='problem_list'),
    path('problems/<int:problem_id>/', problem_detail, name='problem_detail'),
    
]