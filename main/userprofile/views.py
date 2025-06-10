# userprofile/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from problems.models import Problem # Make sure this import path is correct for your Problem model

@login_required
def user_profile(request):
    user = request.user

    total_solved_questions = user.solved_problems.count()

    saved_problems_queryset = user.saved_problems.all()

    # --- Filtering Logic (as before) ---
    search_query = request.GET.get('search', '')
    selected_topic = request.GET.get('topic', '')
    selected_difficulty = request.GET.get('difficulty', '')

    if search_query:
        saved_problems_queryset = saved_problems_queryset.filter(title__icontains=search_query)
    if selected_topic:
        saved_problems_queryset = saved_problems_queryset.filter(topic=selected_topic)
    if selected_difficulty:
        saved_problems_queryset = saved_problems_queryset.filter(difficulty=selected_difficulty)

    # --- NEW: Attach solved status for each problem in the queryset ---
    # Convert queryset to a list to add custom attributes (or use .annotate() for more complex queries)
    saved_problems_list = list(saved_problems_queryset) # Convert to list to modify objects in place

    for problem in saved_problems_list:
        # Use the helper method to check if the current user has solved this problem
        problem.is_solved_by_current_user = problem.get_is_solved_for_user(user)

    # Get all unique topics and difficulties for the filter dropdowns
    all_topics = Problem.objects.values_list('topic', flat=True).distinct().order_by('topic')
    difficulty_order = {'Easy': 1, 'Medium': 2, 'Hard': 3}
    all_difficulties = sorted(list(Problem.objects.values_list('difficulty', flat=True).distinct()), key=lambda x: difficulty_order.get(x, 99))


    context = {
        'total_solved_questions': total_solved_questions,
        'saved_problems': saved_problems_list, # Pass the list with the new attribute
        'search_query': search_query,
        'selected_topic': selected_topic,
        'selected_difficulty': selected_difficulty,
        'all_topics': all_topics,
        'all_difficulties': all_difficulties,
    }

    return render(request, 'user_profile.html', context) # Make sure this path is correct now!

