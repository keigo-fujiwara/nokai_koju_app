from django.contrib import admin
from django.core.management import call_command
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import path
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
    list_display = ['unit', 'source_id', 'text_short', 'parts_count', 'requires_unit_label', 'alternatives_count']
    list_filter = ['unit', 'requires_unit_label', 'parts_count', 'created_at']
    search_fields = ['text', 'correct_answer', 'source_id']
    ordering = ['unit', 'source_id']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('unit', 'source_id', 'text')
        }),
        ('解答設定', {
            'fields': ('correct_answer', 'accepted_alternatives', 'alternatives_display', 'parts_count')
        }),
        ('単位設定', {
            'fields': ('requires_unit_label', 'unit_label_text')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at', 'alternatives_display']
    
    def text_short(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_short.short_description = '問題文'
    
    def alternatives_count(self, obj):
        """別解の数を表示"""
        alternatives = obj.accepted_alternatives or []
        if isinstance(alternatives, str):
            try:
                import json
                alternatives = json.loads(alternatives)
            except json.JSONDecodeError:
                alternatives = []
        
        if not isinstance(alternatives, list):
            alternatives = []
        
        count = len(alternatives)
        if count == 0:
            return 'なし'
        elif count == 1:
            return f'{count}個'
        else:
            return f'{count}個'
    alternatives_count.short_description = '別解数'
    
    def alternatives_display(self, obj):
        """別解を読みやすく表示"""
        alternatives = obj.accepted_alternatives or []
        if isinstance(alternatives, str):
            try:
                import json
                alternatives = json.loads(alternatives)
            except json.JSONDecodeError:
                alternatives = []
        
        if not isinstance(alternatives, list):
            alternatives = []
        
        if not alternatives:
            return '別解なし'
        
        html = '<ul>'
        for i, alt in enumerate(alternatives, 1):
            html += f'<li>{i}. {alt}</li>'
        html += '</ul>'
        
        return html
    alternatives_display.short_description = '別解一覧'
    alternatives_display.allow_tags = True
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sync-from-supabase/', self.admin_site.admin_view(self.sync_from_supabase), name='quiz_app_question_sync_from_supabase'),
        ]
        return custom_urls + urls
    
    def sync_from_supabase(self, request):
        """Supabaseからデータを同期"""
        try:
            # ドライランで実行して結果を確認
            call_command('sync_from_supabase', dry_run=True, verbosity=0)
            
            # 実際の同期を実行
            call_command('sync_from_supabase', verbosity=0)
            
            messages.success(request, 'Supabaseからの同期が完了しました。')
        except Exception as e:
            messages.error(request, f'同期中にエラーが発生しました: {str(e)}')
        
        return HttpResponseRedirect('../')


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
