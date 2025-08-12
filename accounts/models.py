from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """カスタムユーザーモデル"""
    
    class Role(models.TextChoices):
        STUDENT = 'student', '生徒'
        ADMIN = 'admin', '管理者'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name='役割'
    )
    email = models.EmailField(blank=True, verbose_name='メールアドレス')
    
    class Meta:
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class StudentProfile(models.Model):
    """生徒プロファイル"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name='ユーザー'
    )
    
    # 会員番号（8桁）
    member_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{8}$',
                message='会員番号は8桁の数字で入力してください。'
            )
        ],
        verbose_name='会員番号'
    )
    
    prefecture = models.CharField(max_length=10, verbose_name='都道府県')
    school = models.CharField(max_length=100, verbose_name='所属校')
    class_name = models.CharField(max_length=50, verbose_name='クラス')
    nickname = models.CharField(max_length=50, verbose_name='ニックネーム')
    grade = models.CharField(max_length=10, verbose_name='学年')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    
    class Meta:
        verbose_name = '生徒プロファイル'
        verbose_name_plural = '生徒プロファイル'
    
    def __str__(self):
        return f"{self.nickname} ({self.school} {self.class_name})"


class AdminProfile(models.Model):
    """管理者プロファイル"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin_profile',
        verbose_name='ユーザー'
    )
    
    name = models.CharField(max_length=100, verbose_name='名前')
    employee_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='社員番号'
    )
    email = models.EmailField(verbose_name='メールアドレス')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    
    class Meta:
        verbose_name = '管理者プロファイル'
        verbose_name_plural = '管理者プロファイル'
    
    def __str__(self):
        return f"{self.name} ({self.employee_number})"
