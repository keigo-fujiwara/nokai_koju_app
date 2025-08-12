from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # 管理画面ホーム
    path('', views.AdminHomeView.as_view(), name='home'),
    
    # XLSMアップロード
    path('upload/', views.XLSMUploadView.as_view(), name='upload'),
    path('upload/status/', views.UploadStatusView.as_view(), name='upload_status'),
    path('upload/preview/<int:upload_id>/', views.XLSMPreviewView.as_view(), name='upload_preview'),
    path('upload/confirm/<int:upload_id>/', views.XLSMConfirmView.as_view(), name='upload_confirm'),
    
    # 問題管理
    path('questions/', views.QuestionListView.as_view(), name='questions'),
    path('questions/<int:pk>/edit/', views.QuestionEditView.as_view(), name='question_edit'),
    path('questions/<int:pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
    
    # 分析
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('analytics/class/<int:pk>/', views.ClassAnalyticsView.as_view(), name='class_analytics'),
    
    # PDF生成
    path('pdf/generate/<int:pk>/', views.PDFGenerateView.as_view(), name='pdf_generate'),
    
    # 宿題管理
    path('homework/', views.HomeworkListView.as_view(), name='homework_list'),
    path('homework/create/', views.HomeworkCreateView.as_view(), name='homework_create'),
    path('homework/<int:pk>/edit/', views.HomeworkEditView.as_view(), name='homework_edit'),
    path('homework/<int:pk>/delete/', views.HomeworkDeleteView.as_view(), name='homework_delete'),
]
