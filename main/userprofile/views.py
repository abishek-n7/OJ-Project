# userprofile/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from problems.models import Problem

@login_required
def user_profile(request):
    user = request.user
    view_type = request.GET.get("view", "saved")  

    search_query = request.GET.get("search", "")
    selected_topic = request.GET.get("topic", "")
    selected_difficulty = request.GET.get("difficulty", "")

    if view_type == "solved":
        problems = user.solved_problems.all()
    else:
        problems = user.saved_problems.all()

    if search_query:
        problems = problems.filter(title__icontains=search_query)
    if selected_topic:
        problems = problems.filter(topic=selected_topic)
    if selected_difficulty:
        problems = problems.filter(difficulty=selected_difficulty)

    all_topics = Problem.objects.values_list("topic", flat=True).distinct()
    all_difficulties = Problem.objects.values_list("difficulty", flat=True).distinct()

    for problem in problems:
        problem.is_solved_by_current_user = problem.get_is_solved_for_user(user)

    context = {
        "total_solved_questions": user.solved_problems.count(),
        "problems": problems,
        "view_type": view_type,
        "search_query": search_query,
        "selected_topic": selected_topic,
        "selected_difficulty": selected_difficulty,
        "all_topics": all_topics,
        "all_difficulties": all_difficulties,
    }
    return render(request, "user_profile.html", context)

