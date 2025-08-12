from django.urls import path
from . import views

app_name = 'quiz_app'

urlpatterns = [
    # メインページ
    path('', views.HomeView.as_view(), name='home'),
    
    # クイズ関連
    path('subject/<int:pk>/', views.SubjectView.as_view(), name='subject'),
    path('unit/<int:pk>/', views.UnitView.as_view(), name='unit'),
    path('quiz/start/<int:unit_id>/<int:question_count>/', views.QuizStartView.as_view(), name='quiz_start'),
    path('quiz/question/<int:session_id>/<int:question_number>/', views.QuizQuestionView.as_view(), name='quiz_question'),
    path('quiz/result/<int:pk>/', views.QuizResultView.as_view(), name='quiz_result'),
    path('quiz/retry/<int:pk>/', views.QuizRetryView.as_view(), name='quiz_retry'),
    path('quiz/retry/start/<int:pk>/', views.QuizRetryStartView.as_view(), name='quiz_retry_start'),
    
    # API
    path('api/submit-answer/', views.SubmitAnswerView.as_view(), name='api_submit_answer'),
    path('api/quiz-status/<int:pk>/', views.QuizStatusView.as_view(), name='quiz_status'),
    path('quiz/submit/<int:session_id>/<int:question_number>/', views.submit_answer, name='submit_answer'),
    
    # 生徒マイページ
    path('mypage/', views.MyPageView.as_view(), name='mypage'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('ranking/', views.RankingView.as_view(), name='ranking'),
    
    # 宿題
    path('homework/<str:slug>/', views.HomeworkView.as_view(), name='homework'),
]
