from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class XLSMUpload(models.Model):
    """XLSMファイルアップロード記録"""
    
    class Subject(models.TextChoices):
        SCIENCE = 'science', '理科'
        SOCIAL = 'social', '社会'
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='xlsm_uploads',
        verbose_name='アップロード者'
    )
    subject = models.CharField(
        max_length=10,
        choices=Subject.choices,
        verbose_name='教科'
    )
    file = models.FileField(upload_to='xlsm_files/', verbose_name='ファイル')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='アップロード日時')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='処理日時')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '処理待ち'),
            ('processing', '処理中'),
            ('completed', '完了'),
            ('failed', '失敗'),
        ],
        default='pending',
        verbose_name='ステータス'
    )
    error_message = models.TextField(blank=True, verbose_name='エラーメッセージ')
    
    class Meta:
        verbose_name = 'XLSMアップロード'
        verbose_name_plural = 'XLSMアップロード'
    
    def __str__(self):
        return f"{self.get_subject_display()} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"


class AnalyticsData(models.Model):
    """分析データ（キャッシュ用）"""
    
    data_type = models.CharField(max_length=50, verbose_name='データタイプ')
    scope = models.CharField(max_length=100, verbose_name='スコープ')
    data = models.JSONField(verbose_name='データ')
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name='計算日時')
    
    class Meta:
        verbose_name = '分析データ'
        verbose_name_plural = '分析データ'
        unique_together = ['data_type', 'scope']
    
    def __str__(self):
        return f"{self.data_type} - {self.scope}"


class PDFTemplate(models.Model):
    """PDFテンプレート"""
    
    name = models.CharField(max_length=100, verbose_name='テンプレート名')
    template_file = models.FileField(upload_to='pdf_templates/', verbose_name='テンプレートファイル')
    is_active = models.BooleanField(default=True, verbose_name='有効')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    
    class Meta:
        verbose_name = 'PDFテンプレート'
        verbose_name_plural = 'PDFテンプレート'
    
    def __str__(self):
        return self.name


class SystemLog(models.Model):
    """システムログ"""
    
    class Level(models.TextChoices):
        INFO = 'info', '情報'
        WARNING = 'warning', '警告'
        ERROR = 'error', 'エラー'
    
    level = models.CharField(
        max_length=10,
        choices=Level.choices,
        verbose_name='レベル'
    )
    message = models.TextField(verbose_name='メッセージ')
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_logs',
        verbose_name='ユーザー'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    
    class Meta:
        verbose_name = 'システムログ'
        verbose_name_plural = 'システムログ'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_level_display()} - {self.message[:50]}..."
