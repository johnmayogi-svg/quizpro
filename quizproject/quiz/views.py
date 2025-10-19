from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, Choice, QuizAttempt

# ------------------------
# Home & Dashboards
# ------------------------
def home(request):
    return render(request, 'quiz/home.html')

def dashboard(request):
    quiz = Quiz.objects.last()
    now = timezone.localtime()
    return render(request, "quiz/dashboard.html", {"quiz": quiz, "now": now})

@login_required
def user_dashboard(request):
    attempts = request.user.attempts.select_related('quiz').order_by('-completed_at')
    return render(request, 'quiz/user_dashboard.html', {'attempts': attempts})

# ------------------------
# Quiz Views
# ------------------------
def quiz_list(request):
    now = timezone.now()
    quizzes = Quiz.objects.all()  # fetch all quizzes
    return render(request, 'quiz/quiz_list.html', {"quizzes": quizzes, "now": now})

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    now = timezone.now()
    questions = quiz.questions.all()

    # ---------- Timing Checks ----------
    if quiz.start_at and now < quiz.start_at:
        return render(request, "quiz/quiz_not_started.html", {"quiz": quiz})
    if quiz.expire_at and now > quiz.expire_at:
        return render(request, "quiz/quiz_expired.html", {"quiz": quiz})

    # ---------- Handle POST (submission) ----------
    if request.method == "POST":
        score = 0
        user_answers = {}

        for question in questions:
            selected = request.POST.get(f"question_{question.id}")
            user_answers[question.id] = int(selected) if selected else None
            if selected:
                try:
                    choice = question.choices.get(id=selected)
                    if choice.is_correct:
                        score += 1
                except Choice.DoesNotExist:
                    pass

        # Save the attempt
        QuizAttempt.objects.create(user=request.user, quiz=quiz, score=score)

        return render(request, "quiz/quiz_result.html", {
            "quiz": quiz,
            "score": score,
            "total": questions.count(),
            "questions": questions,
            "user_answers": user_answers,
        })

    # ---------- Render Quiz ----------
    return render(request, "quiz/take_quiz.html", {"quiz": quiz, "questions": questions})

# ------------------------
# Authentication
# ------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("user_dashboard")
        else:
            return render(request, "quiz/login.html", {"error": "Invalid credentials"})
    return render(request, "quiz/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")
