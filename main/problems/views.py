from django.shortcuts import render, get_object_or_404, redirect
from problems.models import Problem
from django.http import HttpResponse
from django.template import loader

def problem_list(request):
    problemlist = Problem.objects.all()
    template = loader.get_template("problem_list.html")
    context = {
        'problemlist':problemlist,
    }
    return HttpResponse(template.render(context, request))

"""def problem_detail(request, id):
    req_problem = Problem.objects.get(id=id)
    template = loader.get_template("problem_detail.html")
    context = {
        "req_problem":req_problem,
    }
    return HttpResponse(template.render(context, request))"""

from django.shortcuts import render

def problem_detail(request, id):
    req_problem = Problem.objects.get(id=id)

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

    return render(request, "problem_detail.html", context)

