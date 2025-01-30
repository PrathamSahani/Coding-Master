from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import UserProfile, Dashboard, Question, TestCase_Question, Comment, CodeSubmission
from .models import Contest, TestCase, Submission
import tempfile
import subprocess
import os
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm, UserProfileForm
from django.contrib import messages
from .models import UserProfile
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from datetime import timedelta



# Display all contest details
def home_view(request):
    contests = Contest.objects.all()
    return render(request, 'home_view.html', {'contests': contests, 'user': request.user})

# main home page 
def home(request):
    return render(request, 'home.html')

# display all coding question 
def home_question_view(request):
    questions = Question.objects.all()

    difficulty_filter = request.GET.get('difficulty', '')
    tag_filter = request.GET.get('tag', '')

    # Apply filters if values exist
    if difficulty_filter:
        questions = questions.filter(difficulty=difficulty_filter)
    if tag_filter:
        questions = questions.filter(problem_tag__icontains=tag_filter)

    return render(request, 'home_question.html', {
        'questions': questions,
        'difficulty_filter': difficulty_filter,
        'tag_filter': tag_filter
    })
    
# admin 
def is_admin(user):
    return user.is_authenticated and user.username == "admin"

# admin manage coding question
def admin_question_view(request):
    
    questions = Question.objects.all()
    difficulty_filter = request.GET.get('difficulty', '')
    tag_filter = request.GET.get('tag', '')

    if difficulty_filter:
        questions = questions.filter(difficulty=difficulty_filter)
    if tag_filter:
        questions = questions.filter(problem_tag__icontains=tag_filter)

    return render(request, 'admin_question.html', {
        'questions': questions,
        'difficulty_filter': difficulty_filter,
        'tag_filter': tag_filter
    })

# Predefined admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session["admin_logged_in"] = True
            return redirect("admin_home")
        else:
            return render(request, "admin_login.html", {"error": "Invalid credentials"})

    return render(request, "admin_login.html")

# admin home page
def admin_home(request):
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")
    return render(request, "admin_home.html")

# admin logout method
def admin_logout(request):
    logout(request)
    request.session.flush()
    return redirect("admin_login")


def create_question_view(request):

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        base_code = request.POST.get('base_code')
        difficulty = request.POST.get('difficulty')
        problem_tag = request.POST.get('problem_tag')

        if not problem_tag:
            problem_tag = title.lower().replace(" ", "_")

        question = Question.objects.create(
            title=title,
            description=description,
            base_code=base_code,
            difficulty=difficulty,
            problem_tag=problem_tag
        )

        # Collecting test cases dynamically
        test_case_inputs = [key for key in request.POST.keys() if key.startswith('test_case_input_')]
        for key in test_case_inputs:
            index = key.split('_')[-1]
            input_data = request.POST.get(key)
            expected_output = request.POST.get(f'test_case_output_{index}')
            if input_data and expected_output:
                TestCase_Question.objects.create(
                    question=question,
                    input_data=input_data,
                    expected_output=expected_output
                )

        return redirect('admin_home')
    
    return render(request, 'create_question.html')


# delete question ( only can admin)
def delete_question_view(request, question_id):
  
    question = get_object_or_404(Question, id=question_id)
    question.delete()
    return redirect('admin_question_view')  


# participate/attempt in coding question 
@login_required(login_url='/login/')
def participate_question_view(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    test_cases = TestCase_Question.objects.filter(question=question)

    if request.method == 'POST':
        language = request.POST.get('language')
        code = request.POST.get('code')
        is_submit = request.POST.get('is_submit') == 'true'  # Check if submit button was clicked

        if language not in ['python', 'java', 'cpp']:
            return JsonResponse({'error': 'Unsupported language selected.'}, status=400)

        results = []
        passed = True  

        for test_case in test_cases:
            result = execute_code(language, code, test_case.input_data)
            is_pass = result['output'].strip() == test_case.expected_output.strip()
            results.append({
                'input': test_case.input_data,
                'expected_output': test_case.expected_output,
                'actual_output': result['output'],
                'status': 'pass' if is_pass else 'fail'
            })
            if not is_pass:
                passed = False  

        # Save only if user clicked "Submit"
        if is_submit:
            Dashboard.objects.create(
                user=request.user,
                question=question,
                problem_title=question.title,
                language=language,
                code=code,
                status="Pass" if passed else "Fail"
            )

        return JsonResponse({'results': results})

    return render(request, 'participate_question.html', {'question': question, 'test_cases': test_cases})


# user dashboard
@login_required
def user_dashboard(request):
    dashboards = Dashboard.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, 'dashboard.html', {'dashboards': dashboards})


# user can create own contest
@login_required
def create_contest_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        base_code = request.POST.get('base_code')
        start_date = request.POST.get('start_date')
        duration_minutes = request.POST.get('duration')

        duration = timedelta(minutes=int(duration_minutes)) if duration_minutes else None

        contest = Contest.objects.create(
            title=title,
            description=description,
            base_code=base_code,
            start_date=start_date if start_date else None,
            duration=duration,
            created_by=request.user  # Assign the creator
        )

        # Collecting test cases dynamically
        test_case_inputs = [key for key in request.POST.keys() if key.startswith('test_case_input_')]
        for key in test_case_inputs:
            index = key.split('_')[-1]
            input_data = request.POST.get(key)
            expected_output = request.POST.get(f'test_case_output_{index}')
            if input_data and expected_output:
                TestCase.objects.create(
                    contest=contest,
                    input_data=input_data,
                    expected_output=expected_output
                )

        return redirect('home')
    
    return render(request, 'create_contest.html')

# only contest creator can delete contest 
@login_required
def delete_contest_view(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)

    if request.user == contest.created_by:
        contest.delete()

    return redirect('home')

# participate contest 
@login_required
def participate_contest_view(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    test_cases = TestCase.objects.filter(contest=contest)
    user_submissions = Submission.objects.filter(contest=contest, user=request.user)

    if user_submissions.exists() and user_submissions.filter(is_submit=True).exists():
        return render(request, 'participate_contest.html', {'contest': contest, 'message': 'You have already participated in this contest.'})

    current_time = timezone.now()
    contest_start = contest.start_date
    contest_end = contest_start + contest.duration if contest_start and contest.duration else None

    if contest_start and current_time < contest_start:
        return render(request, 'participate_contest.html', {'contest': contest, 'message': f'Contest starts at {contest_start}.'})
    if contest_end and current_time > contest_end:
        return render(request, 'participate_contest.html', {'contest': contest, 'message': f'Contest ended at {contest_end}.'})

    if request.method == 'POST':
        language = request.POST.get('language')
        code = request.POST.get('code')
        is_submit = request.POST.get('is_submit') == 'true'
        cheating_attempt = int(request.POST.get('cheating_attempt', 0))  # New field for cheating attempts

        if language not in ['python', 'java', 'cpp']:
            return JsonResponse({'error': 'Unsupported language selected.'}, status=400)

        start_execution = timezone.now()
        results = []
        all_passed = True

        for test_case in test_cases:
            result = execute_code(
                language=language, 
                code=code, 
                user_input=test_case.input_data
            )
            status = 'pass' if result['output'].strip() == test_case.expected_output.strip() else 'fail'
            if status == 'fail':
                all_passed = False
            results.append({
                'input': test_case.input_data,
                'expected_output': test_case.expected_output,
                'actual_output': result['output'],
                'status': status
            })

        end_execution = timezone.now()
        time_taken = (end_execution - start_execution).total_seconds()

        test_case_status = 'pass' if all_passed else 'fail'
        
        # Process the submission based on is_submit
        if is_submit:
            submission = Submission.objects.create(
                user=request.user,
                contest=contest,
                code=code,
                language=language,
                is_submit=True,
                time_taken=time_taken, 
                test_case_result=test_case_status
            )

            # Calculate ranking
            passed_submissions = Submission.objects.filter(contest=contest, test_case_result='pass').order_by('time_taken')
            for rank, sub in enumerate(passed_submissions, start=1):
                sub.ranking = rank
                sub.save()

            return JsonResponse({'results': results, 'redirect_url': '/leaderboard/'})
        
        # Handle auto submission due to cheating
        if cheating_attempt >= 3:
            submission = Submission.objects.create(
                user=request.user,
                contest=contest,
                code=code,
                language=language,
                is_submit=True,
                time_taken=time_taken, 
                test_case_result='fail_due_to_cheating'
            )
            # Calculate ranking
            passed_submissions = Submission.objects.filter(contest=contest, test_case_result='pass').order_by('time_taken')
            for rank, sub in enumerate(passed_submissions, start=1):
                sub.ranking = rank
                sub.save()
            return JsonResponse({'redirect_url': '/'}) 

        return JsonResponse({'results': results})
    
    return render(request, 'participate_contest.html', {'contest': contest, 'test_cases': test_cases, 'contest_start': contest_start, 'contest_end': contest_end})

# execute code
def execute_code(language, code, user_input):
    with tempfile.TemporaryDirectory() as temp_dir:
        if language == 'python':
            return execute_python(code, user_input, temp_dir)
        elif language == 'java':
            return execute_java(code, user_input, temp_dir)
        elif language == 'cpp':
            return execute_cpp(code, user_input, temp_dir)
    return {"output": "Unsupported language"}

# execute python code
def execute_python(code, user_input, temp_dir):
    try:
        file_path = os.path.join(temp_dir, "main.py")
        with open(file_path, "w") as file:
            file.write(code)

        process = subprocess.run(
            ["python", file_path],
            input=user_input.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        output = process.stdout.decode()
        error = process.stderr.decode()
        if error:
            return {"output": error}
        return {"output": output}
    except Exception as e:
        return {"output": str(e)}


# execute java code 
def execute_java(code, user_input, temp_dir):
    try:
        file_path = os.path.join(temp_dir, "Main.java")
        with open(file_path, "w") as file:
            file.write(code)

        compile_process = subprocess.run(
            ["javac", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        if compile_process.returncode != 0:
            return {"output": compile_process.stderr.decode()}

        class_path = temp_dir
        run_process = subprocess.run(
            ["java", "-cp", class_path, "Main"],
            input=user_input.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        output = run_process.stdout.decode()
        error = run_process.stderr.decode()
        if error:
            return {"output": error}
        return {"output": output}
    except Exception as e:
        return {"output": str(e)}

# execute cpp code
def execute_cpp(code, user_input, temp_dir):
    try:
        file_path = os.path.join(temp_dir, "main.cpp")
        with open(file_path, "w") as file:
            file.write(code)

        executable_path = os.path.join(temp_dir, "main")
        compile_process = subprocess.run(
            ["g++", file_path, "-o", executable_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        if compile_process.returncode != 0:
            return {"output": compile_process.stderr.decode()}

        run_process = subprocess.run(
            [executable_path],
            input=user_input.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        output = run_process.stdout.decode()
        error = run_process.stderr.decode()
        if error:
            return {"output": error}
        return {"output": output}
    except Exception as e:
        return {"output": str(e)}

# compile coding function
def online_code(language, code, user_input):
    with tempfile.TemporaryDirectory() as temp_dir:
        if language == 'python':
            return online_python(code, user_input, temp_dir)
        elif language == 'java':
            return online_java(code, user_input, temp_dir)
        elif language == 'cpp':
            return online_cpp(code, user_input, temp_dir)
    return "Unsupported language"


# compile python code run 
def online_python(code, user_input, temp_dir):
    try:
        file_path = os.path.join(temp_dir, 'code.py')
        with open(file_path, 'w') as file:
            file.write(code)
        
        process = subprocess.Popen(['python', file_path],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        try:
            stdout, stderr = process.communicate(input=user_input, timeout=5)
            if process.returncode == 0:
                return stdout
            return f"Error: {stderr}"
        except subprocess.TimeoutExpired:
            process.kill()
            return "Error: Execution timed out"
    except Exception as e:
        return f"Error: {str(e)}"

# compiler java code run
def online_java(code, user_input, temp_dir):
    try:
        class_name = "Main"
        file_path = os.path.join(temp_dir, f'{class_name}.java')
        
        with open(file_path, 'w') as file:
            file.write(code)
        
        # Compile
        compile_result = subprocess.run(['javac', file_path], 
                                      capture_output=True,
                                      text=True)
        
        if compile_result.returncode != 0:
            return f"Compilation Error: {compile_result.stderr}"
        
        # Run
        process = subprocess.Popen(['java', '-cp', temp_dir, class_name],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        try:
            stdout, stderr = process.communicate(input=user_input, timeout=5)
            if process.returncode == 0:
                return stdout
            return f"Runtime Error: {stderr}"
        except subprocess.TimeoutExpired:
            process.kill()
            return "Error: Execution timed out"
    except Exception as e:
        return f"Error: {str(e)}"

# compiler cpp code run
def online_cpp(code, user_input, temp_dir):
    try:
        source_path = os.path.join(temp_dir, 'code.cpp')
        exe_path = os.path.join(temp_dir, 'code.exe')
        
        with open(source_path, 'w') as file:
            file.write(code)
        
        # Compile
        compile_result = subprocess.run(['g++', source_path, '-o', exe_path], 
                                      capture_output=True,
                                      text=True)
        
        if compile_result.returncode != 0:
            return f"Compilation Error: {compile_result.stderr}"
        
        # Run
        process = subprocess.Popen([exe_path],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        try:
            stdout, stderr = process.communicate(input=user_input, timeout=5)
            if process.returncode == 0:
                return stdout
            return f"Runtime Error: {stderr}"
        except subprocess.TimeoutExpired:
            process.kill()
            return "Error: Execution timed out"
    except Exception as e:
        return f"Error: {str(e)}"


# leaderboard_view
@login_required
def leaderboard_view(request):
    contests = Contest.objects.all()
    selected_contest = None
    submissions = []

    if request.method == 'GET' and 'contest_id' in request.GET:
        contest_id = request.GET.get('contest_id')
        selected_contest = get_object_or_404(Contest, id=contest_id)
        submissions = Submission.objects.filter(contest=selected_contest).order_by('ranking')

    return render(request, 'leaderboard.html', {
        'contests': contests,
        'selected_contest': selected_contest,
        'submissions': submissions
    })
     
# View for showing the user profile ( only username, email and picture)
@login_required
def view_user_profile(request, username):
    user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=user)
    return render(request, 'view_user_profile.html', {'user': user, 'profile': user_profile})


# register user
def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "Registration successful!")
            return redirect('login')
    else:
        user_form = UserRegisterForm()
        profile_form = UserProfileForm()
    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})

# login user 
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials!")
    return render(request, 'login.html')

#logout user
def user_logout(request):
    logout(request)
    return redirect('home')

# view profile details
@login_required
def view_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    contests = Contest.objects.all()  
    submissions = Submission.objects.filter(user=request.user) 
    
    # Calculate contest statistics
    attempted = 0
    unattempted = 0
    passed = 0
    failed = 0

    for contest in contests:
        # Check if the user has attempted the contest
        submission = submissions.filter(contest=contest).first()
        if submission:
            attempted += 1
            if submission.test_case_result == 'pass':
                passed += 1
            else:
                failed += 1
        else:
            unattempted += 1

    # Pass the data to the template
    return render(request, "view_profile.html", {
        "user": request.user,
        "profile": user_profile,
        "attempted": attempted,
        "unattempted": unattempted,
        "passed": passed,
        "failed": failed
    })


# update profile picture
@login_required
def update_profile(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk, user=request.user)  
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("view_profile")
    else:
        form = UserProfileForm(instance=profile)
    return render(request, "update_profile.html", {"form": form})

# delete profile
@login_required
def delete_profile(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk, user=request.user)  
    if request.method == "POST":
        profile.user.delete()
        return redirect("home")
    return render(request, "confirm_delete_profile.html", {"profile": profile})

# discussion view 
def discussion_view(request):
    comments = Comment.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        # Add a new comment ( only authenticated user )
        content = request.POST.get('content')
        comment = Comment.objects.create(user=request.user, content=content)
        return JsonResponse({'status': 'success', 'comment_id': comment.id, 'content': comment.content, 'username': comment.user.username})

    return render(request, 'discussion.html', {'comments': comments})

# edit comment 
@login_required
def edit_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if comment.user == request.user:
        if request.method == 'POST':
            content = request.POST.get('content')
            comment.content = content
            comment.save()
            return JsonResponse({
                'status': 'success', 
                'content': comment.content,
                'username': comment.user.username  # Ensure the username is returned
            })
    return JsonResponse({'status': 'error', 'message': 'You can only edit your own comments.'})

# delete comment
@login_required
def delete_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if comment.user == request.user:
        comment.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'You can only delete your own comments.'})


# online compiler
def compiler_view(request):
    if request.method == 'POST':
        language = request.POST.get('language')
        code = request.POST.get('code')
        user_input = request.POST.get('input', '')
        
        # Create a CodeSubmission instance
        submission = CodeSubmission.objects.create(
            language=language,
            code=code
        )
        
        result = online_code(language, code, user_input)
        submission.result = result
        submission.save()
        
        return JsonResponse({'result': result})
    
    return render(request, 'compiler.html')
