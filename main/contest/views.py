from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Q 

# Import your models from the problems app and contest app
from problems.models import Problem 
from compiler.views import run_code 
from compiler.models import CodeSubmission 
from .models import Contest 

@login_required(login_url='/login/')
def contest_list(request):
    
    contests = Contest.objects.all()

    context = {
        "contestlist": contests,
    }
    return render(request, "contest_list.html", context)


@login_required(login_url='/login/')
def contest_problem_list(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    # Get all problems associated with this contest
    # Assuming Contest has a ManyToManyField called 'problems' to the Problem model
    contest_problems = contest.problems.all().order_by('id') # Order by ID for consistent display

    # For each problem in the contest, determine if the current user has solved it
    # within the context of this contest.
    for problem in contest_problems:
        # Check if the user has a successful submission for this specific problem in this contest
        # This assumes CodeSubmission links to Problem and has a 'verdict' field.
        context = {
            "contest_id": contest_id,
            "contest_name": contest.name,
            "contest_problemlist": contest_problems,
        }
    return render(request, "contest_problem_list.html", context)


@login_required(login_url='/login/')
def contest_problem_detail(request, contest_id, problem_id):
    """
    Displays the detail page for a problem within a specific contest.
    Allows users to view description, test cases, and submit/run code.
    """
    contest = get_object_or_404(Contest, id=contest_id)
    req_problem = get_object_or_404(Problem, id=problem_id)

    # Optional: Verify that the problem actually belongs to this contest
    if req_problem not in contest.problems.all():
        messages.error(request, "This problem does not belong to the specified contest.")
        return redirect('contest_problem_list', contest_id=contest_id)

    input_lines = req_problem.input_testcase.strip().split('\n')
    output_lines = req_problem.output_testcase.strip().split('\n')
    explanations = req_problem.testcase_explanation.strip().split('\n') if req_problem.testcase_explanation else []

    testcases = []
    # Displaying only the first two test cases as examples
    for i in range(min(len(input_lines), 2)):
        input_line = input_lines[i]
        output_line = output_lines[i] if i < len(output_lines) else ''
        explanation_line = explanations[i] if i < len(explanations) else ''
        testcases.append((input_line, output_line, explanation_line))

    context = {
        "contest_id": contest_id, # Pass contest_id for navigation back to contest problem list
        "req_problem": req_problem,
        "testcases": testcases,
    }

    return render(request, "contest_problem_detail.html", context)
