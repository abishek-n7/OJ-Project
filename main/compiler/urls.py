from django.urls import path
from . import views

urlpatterns = [
    path("handle/<int:problem_id>/", views.handle_code, name="handle_code"),
]
