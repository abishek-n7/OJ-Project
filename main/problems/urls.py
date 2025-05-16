from django.urls import path
from problems.views import problem_list, problem_detail

urlpatterns = [
    path('', problem_list), 
    path('problems/', problem_list, name='problem_list'),
    path('problems/<int:id>/', problem_detail, name='problem_detail'),
    
]