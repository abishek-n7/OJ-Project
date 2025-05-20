from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from compiler.forms import CodeSubmissionForm
from django.conf import settings
import os
import uuid
import subprocess
from pathlib import Path
from problems.models import Problem

def normalize_output(output):
    return [line.strip() for line in output.strip().splitlines() if line.strip()]

def handle_code(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)

    input_lines = problem.input_testcase.strip().split('\n')
    output_lines = problem.output_testcase.strip().split('\n')
    explanations = problem.testcase_explanation.strip().split('\n') if problem.testcase_explanation else []

    testcases = []
    for i in range(len(input_lines)):
        input_line = input_lines[i] if i < len(input_lines) else ''
        output_line = output_lines[i] if i < len(output_lines) else ''
        explanation_line = explanations[i] if i < len(explanations) else ''
        testcases.append((input_line, output_line, explanation_line))

    if request.method == "POST":
        action = request.POST.get("action") 
        language = request.POST.get("language")
        code = request.POST.get("code")

        input_data = problem.input_testcase.strip()

        run_all = action == "submit"
        output = run_code(language, code, input_data, run_all=run_all)

        context = {
            "req_problem": problem,
            "testcases": testcases,
            "submitted": True,
            "action": action,
            "language": language,
            "code": code,
            "output": output,
        }

        if action == "submit":
            expected_lines = normalize_output(problem.output_testcase)
            actual_lines = normalize_output(output)

            verdict = "Success" if expected_lines == actual_lines else "Wrong Answer"
            context["verdict"] = verdict

            if verdict == "Wrong Answer":
                # Find first mismatch
                for i, (exp, act) in enumerate(zip(expected_lines, actual_lines)):
                    if exp != act:
                        context["first_failed_output"] = f"Expected: {exp}\nGot: {act}"
                        break
                else:
                    # If expected is longer than actual or vice versa
                    if len(expected_lines) != len(actual_lines):
                        extra = "Missing Output" if len(actual_lines) < len(expected_lines) else "Extra Output"
                        context["first_failed_output"] = f"{extra}\nExpected: {expected_lines}\nGot: {actual_lines}"


        return render(request, "problem_detail.html", context)

    return redirect("problem_detail", problem_id=problem_id)




def submit(request, problem_id):  
    problem = Problem.objects.get(id=problem_id)

    if request.method == "POST":
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.input_data = problem.input_testcase  
            submission.save()

            output = run_code(submission.language, submission.code, submission.input_data)
            submission.output_data = output
            submission.save()

            return render(request, "problem_detail.html", {
                "req_problem": problem, 
                "submitted": True,
                "action": "submit",
                "language": submission.language,
                "code": submission.code,
                "output": output,
                "verdict": "Success" if output.strip() == problem.output_testcase.strip() else "Wrong Answer"
            })

    else:
        form = CodeSubmissionForm()
    return render(request, "problem_detail.html")


def run_code(language, code, input_data, run_all=True):
    if language == "python":
        language = "py"
    
    from pathlib import Path
    import subprocess
    import uuid
    from django.conf import settings

    base_path = Path(settings.BASE_DIR)
    codes_dir = base_path / "codes"
    codes_dir.mkdir(parents=True, exist_ok=True)

    results = []
    testcases = input_data.strip().splitlines()
    testcases_to_run = testcases if run_all else testcases[:2]

    for testcase in testcases_to_run:
        unique = str(uuid.uuid4())
        code_file = codes_dir / f"{unique}.{language}"
        input_file = codes_dir / f"{unique}.in"
        output_file = codes_dir / f"{unique}.out"

        # Save user code and testcase
        with open(code_file, "w") as f:
            f.write(code)
        with open(input_file, "w") as f:
            f.write(testcase)

        # Execution
        if language == "cpp":
            exe_file = codes_dir / f"{unique}.out.exe"
            compile = subprocess.run(["g++", str(code_file), "-o", str(exe_file)])
            if compile.returncode != 0:
                results.append("Compilation Error")
                continue
            with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
                subprocess.run([str(exe_file)], stdin=f_in, stdout=f_out)
        elif language == "py":
            with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
                run = subprocess.run(
                    ["python3", str(code_file)],
                    stdin=f_in,
                    stdout=f_out,
                    stderr=subprocess.PIPE
                )
                if run.returncode != 0:
                    results.append("Runtime Error: " + run.stderr.decode())
                    continue
        else:
            results.append("Language not supported")
            continue

        with open(output_file, "r") as f:
            results.append(f.read().strip())

    return "\n".join(results)
