from django.contrib import admin
from .models import Subject, Unit, Question, QuizSession, QuizAttempt, Homework


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'label_ja']
    search_fields = ['code', 'label_ja']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['subject', 'grade_year', 'category', 'unit_key']
    list_filter = ['subject', 'grade_year']
    search_fields = ['category', 'unit_key']
    ordering = ['subject', 'grade_year', 'category']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['unit', 'source_id', 'text_short', 'parts_count', 'requires_unit_label']
    list_filter = ['unit', 'requires_unit_label', 'parts_count', 'created_at']
    search_fields = ['text', 'correct_answer', 'source_id']
    ordering = ['unit', 'source_id']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('unit', 'source_id', 'text')
        }),
        ('解答設定', {
            'fields': ('correct_answer', 'accepted_alternatives', 'parts_count')
        }),
        ('単位設定', {
            'fields': ('requires_unit_label', 'unit_label_text')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def text_short(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_short.short_description = '問題文'


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'unit', 'question_count', 'started_at', 'finished_at', 'total_score']
    list_filter = ['unit', 'question_count', 'started_at']
    search_fields = ['user__username', 'unit__unit_key']
    ordering = ['-started_at']
    readonly_fields = ['started_at', 'finished_at']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['session', 'question', 'is_correct', 'time_spent_sec', 'created_at']
    list_filter = ['is_correct', 'created_at']
    search_fields = ['session__user__username', 'question__text']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ['unit', 'question_count', 'publish_scope', 'is_published', 'created_by']
    list_filter = ['publish_scope', 'is_published', 'created_at']
    search_fields = ['unit__unit_key', 'public_slug']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('created_by', 'unit', 'question_count')
        }),
        ('公開設定', {
            'fields': ('publish_scope', 'scope_prefecture', 'scope_school', 'scope_class_name')
        }),
        ('公開状態', {
            'fields': ('is_published', 'published_at', 'public_slug')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
