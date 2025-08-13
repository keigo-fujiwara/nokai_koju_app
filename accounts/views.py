import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from .models import User, StudentProfile, AdminProfile
from .forms import StudentRegistrationForm, AdminRegistrationForm, ProfileEditForm


def send_activation_email_async(user, request):
    """非同期でメール認証用のメールを送信"""
    def send_email():
        try:
            from django.conf import settings
            
            mail_subject = '管理者アカウント認証メール'
            
            # 開発環境では直接URLを生成
            if settings.DEBUG:
                domain = '127.0.0.1:8000'
            else:
                current_site = get_current_site(request)
                domain = current_site.domain
            
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # メール本文のテンプレート
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': domain,
                'uid': uid,
                'token': token,
            })
            
            # メール送信
            send_mail(
                mail_subject,
                message,
                'noreply@example.com',  # 送信者
                [user.email],  # 受信者
                fail_silently=False,
            )
            print(f"DEBUG: メール送信完了 - {user.email}")
        except Exception as e:
            print(f"DEBUG: メール送信エラー - {e}")
    
    # 非同期でメール送信を実行
    thread = threading.Thread(target=send_email)
    thread.daemon = True
    thread.start()


def send_activation_email(user, request):
    """メール認証用のメールを送信（同期版 - 後方互換性のため）"""
    from django.conf import settings
    
    mail_subject = '管理者アカウント認証メール'
    
    # 開発環境では直接URLを生成
    if settings.DEBUG:
        domain = '127.0.0.1:8000'
    else:
        current_site = get_current_site(request)
        domain = current_site.domain
    
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    
    # メール本文のテンプレート
    message = render_to_string('accounts/activation_email.html', {
        'user': user,
        'domain': domain,
        'uid': uid,
        'token': token,
    })
    
    # メール送信
    send_mail(
        mail_subject,
        message,
        'noreply@example.com',  # 送信者
        [user.email],  # 受信者
        fail_silently=False,
    )


def activate_account(request, uidb64, token):
    """メール認証リンクをクリックした時の処理"""
    from django.conf import settings
    
    print(f"DEBUG: activate_account called with uidb64={uidb64}, token={token}")
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        print(f"DEBUG: Decoded uid={uid}")
        user = User.objects.get(pk=uid)
        print(f"DEBUG: User found - ID: {user.pk}, Username: {user.username}, Active: {user.is_active}")
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        user = None
        print(f"DEBUG: User not found - Error: {e}")
    
    if user is not None:
        # トークンの有効性をチェック
        token_valid = default_token_generator.check_token(user, token)
        print(f"DEBUG: Token validation - Valid: {token_valid}")
        
        if token_valid:
            # ユーザーをアクティブにする
            user.is_active = True
            user.save()
            print(f"DEBUG: User activated - ID: {user.pk}, Active: {user.is_active}")
            messages.success(request, 'アカウントが正常に認証されました。ログインしてください。')
            return redirect('accounts:login')
        else:
            print(f"DEBUG: Token invalid for user {user.pk}")
            # トークンが無効な場合、ユーザーを手動でアクティブにする（開発環境用）
            if settings.DEBUG:
                print(f"DEBUG: Development mode - manually activating user {user.pk}")
                user.is_active = True
                user.save()
                messages.success(request, 'アカウントが正常に認証されました。ログインしてください。')
                return redirect('accounts:login')
            else:
                messages.error(request, '認証リンクが無効です。')
                return redirect('accounts:login')
    else:
        print(f"DEBUG: No user found for uidb64: {uidb64}")
        messages.error(request, '認証リンクが無効です。')
        return redirect('accounts:login')


class StudentRegisterView(CreateView):
    model = User
    form_class = StudentRegistrationForm
    template_name = 'accounts/student_register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        with transaction.atomic():
            user = form.save(commit=False)
            user.role = User.Role.STUDENT
            user.save()
            
            # 生徒プロファイルを作成
            StudentProfile.objects.create(
                user=user,
                member_id=form.cleaned_data['member_id'],
                prefecture=form.cleaned_data['prefecture'],
                school=form.cleaned_data['school'],
                class_name=form.cleaned_data['class_name'],
                nickname=form.cleaned_data['nickname'],
                grade=form.cleaned_data['grade']
            )
        
        messages.success(self.request, '生徒アカウントが正常に作成されました。ログインしてください。')
        return super().form_valid(form)


class AdminRegisterView(CreateView):
    model = User
    form_class = AdminRegistrationForm
    template_name = 'accounts/admin_register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        with transaction.atomic():
            user = form.save(commit=False)
            user.role = User.Role.ADMIN
            user.is_active = False  # メール確認後に有効化
            user.save()
            
            # 管理者プロファイルを作成
            AdminProfile.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                employee_number=form.cleaned_data['employee_number'],
                email=form.cleaned_data['email']
            )
            
            # メール認証メールを送信
            try:
                from django.conf import settings
                
                if settings.DEBUG:
                    # 開発環境: 即座に認証してメール送信は非同期で
                    user.is_active = True
                    user.save()
                    send_activation_email_async(user, self.request)
                    messages.success(self.request, '管理者アカウントが作成されました。開発環境のため即座に認証されました。')
                else:
                    # 本番環境: メール認証が必要
                    send_activation_email_async(user, self.request)
                    messages.success(self.request, '管理者アカウントが作成されました。メール確認後にログインできます。')
            except Exception as e:
                # メール送信に失敗した場合、アカウントを削除
                user.delete()
                messages.error(self.request, 'メール送信に失敗しました。もう一度お試しください。')
                return self.form_invalid(form)
        
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    
    def get_object(self):
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'プロファイルが更新されました。')
        return super().form_valid(form)
