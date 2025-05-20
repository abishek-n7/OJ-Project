from django.shortcuts import render, get_object_or_404, redirect
from problems.models import Problem
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from compiler.views import run_code
from compiler.models import CodeSubmission
from django.db.models import Q

from django.db.models import Q

@login_required(login_url='/login/')
def problem_list(request):
    search_query = request.GET.get("search", "")
    selected_topic = request.GET.get("topic", "")
    selected_difficulty = request.GET.get("difficulty", "")
    solved_filter = request.GET.get("solved", "")

    problems = Problem.objects.all()

    if search_query:
        problems = problems.filter(title__icontains=search_query)

    if selected_topic:
        problems = problems.filter(topic=selected_topic)

    if selected_difficulty:
        problems = problems.filter(difficulty=selected_difficulty)

    if solved_filter == "solved":
        problems = problems.filter(isSolved=True)
    elif solved_filter == "unsolved":
        problems = problems.filter(isSolved=False)

    all_topics = Problem.objects.values_list("topic", flat=True).distinct()
    all_difficulties = Problem.objects.values_list("difficulty", flat=True).distinct()

    context = {
        "problemlist": problems,
        "search_query": search_query,
        "selected_topic": selected_topic,
        "selected_difficulty": selected_difficulty,
        "solved_filter": solved_filter,
        "all_topics": all_topics,
        "all_difficulties": all_difficulties,
    }

    return render(request, "problem_list.html", context)





@login_required(login_url='/login/')
def problem_detail(request, problem_id):
    req_problem = Problem.objects.get(id=problem_id)

    input_lines = req_problem.input_testcase.strip().split('\n')
    output_lines = req_problem.output_testcase.strip().split('\n')
    explanations = req_problem.testcase_explanation.strip().split('\n') if req_problem.testcase_explanation else []

    testcases = []
    for i in range(len(input_lines)):
        input_line = input_lines[i] if i < len(input_lines) else ''
        output_line = output_lines[i] if i < len(output_lines) else ''
        explanation_line = explanations[i] if i < len(explanations) else ''
        testcases.append((input_line, output_line, explanation_line))

    context = {
        "req_problem": req_problem,
        "testcases": testcases,
    }

    if request.method == "POST":
        language = request.POST.get("language")
        code = request.POST.get("code")
        action = request.POST.get("action")

        input_data = req_problem.input_testcase.strip()
        output_data = run_code(language, code, input_data)

        context.update({
            "submitted": True,
            "language": language,
            "code": code,
            "output": output_data,
            "action": action,
        })

    return render(request, "problem_detail.html", context)
