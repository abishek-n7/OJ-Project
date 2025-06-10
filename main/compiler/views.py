from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from compiler.forms import CodeSubmissionForm
from django.conf import settings
import os
import uuid
import subprocess
from pathlib import Path
from problems.models import Problem
import google.generativeai as genai
from dotenv import load_dotenv
import os
from pathlib import Path
import subprocess
import uuid
from django.conf import settings

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

def normalize_output(output):
    return [line.strip() for line in output.strip().splitlines() if line.strip()]

def get_ai_review(code, language, problem):
    prompt = f"""
You are reviewing a code submission for a programming problem. Ensure there is LESS THAN 12 words per line in output text, check language compatibility

### Problem Statement:
{problem.description}

### Constraints:
{problem.constraints}

### Sample Input:
{problem.input_testcase}

### Expected Output:
{problem.output_testcase}

### Explanation:
{problem.testcase_explanation}

### User's {language} Code:
{code}

Please provide:
- Code correctness evaluation
- Any potential logic issues or edge cases
- Suggestions for optimization
- Adherence to best practices
- Readability improvements
- Dont give the corrected code. Let user do it himself
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash") 
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


def handle_code(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)

    input_lines = problem.input_testcase.strip().split('\n')
    output_lines = problem.output_testcase.strip().split('\n')
    explanations = problem.testcase_explanation.strip().split('\n') if problem.testcase_explanation else []

    testcases = list(zip(input_lines, output_lines, explanations))

    if request.method == "POST":
        action = request.POST.get("action") 
        language = request.POST.get("language")
        code = request.POST.get("code")
        custom_input = request.POST.get("custom_input", "").strip()

        if action == "ai_review":
            review = get_ai_review(code, language, problem)
            return render(request, "problem_detail.html", {
                "req_problem": problem,
                "code": code,
                "custom_input": custom_input,
                "submitted": True,
                "action": action,
                "ai_review": review,
                "language": language,
                "testcases": testcases,
            })


        if action == "run":
            default_lines = problem.input_testcase.strip().splitlines()[:2]
            custom_lines = custom_input.strip().splitlines() if custom_input else []
            input_data = "\n".join(default_lines + custom_lines)
            run_all = True  
        else:
            input_data = problem.input_testcase.strip()
            run_all = True  




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
            "custom_input": custom_input,
        }

        if action == "submit":
            expected_lines = normalize_output(problem.output_testcase)
            actual_lines = normalize_output(output)

            verdict = "Success" if expected_lines == actual_lines else "Wrong Answer"
            context["verdict"] = verdict

            if verdict == "Success": # This is the condition from your snippet
                problem = get_object_or_404(Problem, id=problem_id) # Ensure you have the problem object
                user = request.user # Get the current logged-in user

                # Check if the user hasn't already solved this problem
                if not problem.get_is_solved_for_user(user): # Using the helper method
                    problem.solved_by.add(user) # Mark as solved for this specific user

            if verdict == "Wrong Answer":
                for i, (exp, act) in enumerate(zip(expected_lines, actual_lines)):
                    if exp != act:
                        context["first_failed_output"] = f"Expected: {exp}\nGot: {act}"
                        break
                else:
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

    base_path = Path(settings.BASE_DIR)
    codes_dir = base_path / "codes"
    codes_dir.mkdir(parents=True, exist_ok=True)

    results = []
    testcases = input_data.strip().splitlines()

    testcases_to_run = testcases

    for testcase in testcases_to_run:
        unique = str(uuid.uuid4())
        code_file = codes_dir / f"{unique}.{language}"
        input_file = codes_dir / f"{unique}.in"
        output_file = codes_dir / f"{unique}.out"

        with open(code_file, "w") as f:
            f.write(code)
        with open(input_file, "w") as f:
            f.write(testcase)

        if language == "cpp":
            exe_file = codes_dir / f"{unique}.out.exe"
            compile = subprocess.run(["g++", str(code_file), "-o", str(exe_file)])
            if compile.returncode != 0:
                results.append("Compilation Error")
                continue
            try:
                with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
                    subprocess.run([str(exe_file)], stdin=f_in, stdout=f_out, timeout=3)
            except subprocess.TimeoutExpired:
                results.append("Time Limit Exceeded")
                continue
        elif language == "py":
            try:
                with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
                    run = subprocess.run(
                        ["python3", str(code_file)],
                        stdin=f_in,
                        stdout=f_out,
                        stderr=subprocess.PIPE,
                        timeout=3
                    )
                if run.returncode != 0:
                    results.append("Runtime Error: " + run.stderr.decode())
                    continue
            except subprocess.TimeoutExpired:
                results.append("Time Limit Exceeded")
                continue
        else:
            results.append("Language not supported")
            continue

        with open(output_file, "r") as f:
            results.append(f.read().strip())

    return "\n".join(results)
