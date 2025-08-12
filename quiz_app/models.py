from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import json

User = get_user_model()


class Subject(models.Model):
    """教科（理科/社会）"""
    
    class Code(models.TextChoices):
        SCIENCE = 'science', '理科'
        SOCIAL = 'social', '社会'
    
    code = models.CharField(
        max_length=10,
        choices=Code.choices,
        unique=True,
        verbose_name='教科コード'
    )
    label_ja = models.CharField(max_length=20, verbose_name='教科名')
    
    class Meta:
        verbose_name = '教科'
        verbose_name_plural = '教科'
    
    def __str__(self):
        return self.label_ja


class Unit(models.Model):
    """単元"""
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='units',
        verbose_name='教科'
    )
    grade_year = models.CharField(max_length=10, verbose_name='学年')
    category = models.CharField(max_length=50, verbose_name='カテゴリ')
    unit_key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='単元キー'
    )
    
    class Meta:
        verbose_name = '単元'
        verbose_name_plural = '単元'
        unique_together = ['subject', 'grade_year', 'category']
    
    def __str__(self):
        return f"{self.subject.label_ja} - {self.grade_year} - {self.category}"
    
    def save(self, *args, **kwargs):
        if not self.unit_key:
            self.unit_key = f"{self.subject.label_ja}-{self.grade_year}-{self.category}"
        super().save(*args, **kwargs)


class Question(models.Model):
    """問題"""
    
    class QuestionType(models.TextChoices):
        TEXT = 'text', '記述問題'
        CHOICE = 'choice', '選択問題'
    
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='単元'
    )
    source_id = models.CharField(max_length=50, verbose_name='元データID')
    question_type = models.CharField(
        max_length=10,
        choices=QuestionType.choices,
        default=QuestionType.TEXT,
        verbose_name='問題タイプ'
    )
    text = models.TextField(verbose_name='問題文')
    correct_answer = models.TextField(verbose_name='正解')
    accepted_alternatives = models.JSONField(
        default=list,
        blank=True,
        verbose_name='別解'
    )
    # 選択問題用の選択肢
    choices = models.JSONField(
        default=list,
        blank=True,
        verbose_name='選択肢'
    )
    requires_unit_label = models.BooleanField(
        default=False,
        verbose_name='単位ラベル必要'
    )
    unit_label_text = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='単位ラベル'
    )
    parts_count = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='解答欄数'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    
    class Meta:
        verbose_name = '問題'
        verbose_name_plural = '問題'
        unique_together = ['unit', 'source_id']
        indexes = [
            models.Index(fields=['unit', 'source_id']),
        ]
    
    def __str__(self):
        return f"{self.unit} - {self.text[:50]}..."


class QuizSession(models.Model):
    """クイズセッション"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_sessions',
        verbose_name='ユーザー'
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='quiz_sessions',
        verbose_name='単元'
    )
    question_count = models.PositiveIntegerField(
        choices=[(10, '10問'), (20, '20問')],
        verbose_name='問題数'
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='開始時刻')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='終了時刻')
    total_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='総得点'
    )
    question_ids = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='問題IDマッピング'
    )
    choice_mappings = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='選択肢並べ替えマッピング'
    )
    
    class Meta:
        verbose_name = 'クイズセッション'
        verbose_name_plural = 'クイズセッション'
    
    def __str__(self):
        return f"{self.user.username} - {self.unit} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"


class QuizAttempt(models.Model):
    """クイズ解答記録"""
    
    session = models.ForeignKey(
        QuizSession,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='セッション'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='問題'
    )
    answer_text = models.TextField(verbose_name='解答内容')
    is_correct = models.BooleanField(verbose_name='正解')
    time_spent_sec = models.PositiveIntegerField(verbose_name='解答時間（秒）')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    
    class Meta:
        verbose_name = 'クイズ解答記録'
        verbose_name_plural = 'クイズ解答記録'
        indexes = [
            models.Index(fields=['question']),
        ]
    
    def __str__(self):
        return f"{self.session.user.username} - {self.question.text[:30]}... - {'正解' if self.is_correct else '不正解'}"


class Homework(models.Model):
    """宿題"""
    
    class PublishScope(models.TextChoices):
        CLASS = 'class', 'クラス'
        SCHOOL = 'school', '学校'
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_homeworks',
        verbose_name='作成者'
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='homeworks',
        verbose_name='単元'
    )
    question_count = models.PositiveIntegerField(verbose_name='問題数')
    publish_scope = models.CharField(
        max_length=10,
        choices=PublishScope.choices,
        verbose_name='公開範囲'
    )
    scope_prefecture = models.CharField(max_length=10, verbose_name='対象都道府県')
    scope_school = models.CharField(max_length=100, verbose_name='対象学校')
    scope_class_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='対象クラス'
    )
    is_published = models.BooleanField(default=False, verbose_name='公開中')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='公開日時')
    public_slug = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='公開スラッグ'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    
    class Meta:
        verbose_name = '宿題'
        verbose_name_plural = '宿題'
    
    def __str__(self):
        return f"{self.unit} - {self.question_count}問 - {self.get_publish_scope_display()}"
