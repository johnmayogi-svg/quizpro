from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # dashboard must exist
    path('quizzes/', views.quiz_list, name='quiz_list'),  # add this
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
]
