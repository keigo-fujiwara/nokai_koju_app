from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # 認証関連
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # ユーザー登録
    path('register/student/', views.StudentRegisterView.as_view(), name='student_register'),
    path('register/admin/', views.AdminRegisterView.as_view(), name='admin_register'),
    
    # プロファイル
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    
    # メール認証
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
]
