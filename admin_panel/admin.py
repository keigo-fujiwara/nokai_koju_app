from django.contrib import admin
from .models import XLSMUpload, AnalyticsData, PDFTemplate, SystemLog


@admin.register(XLSMUpload)
class XLSMUploadAdmin(admin.ModelAdmin):
    list_display = ['subject', 'uploaded_by', 'uploaded_at', 'status', 'processed_at']
    list_filter = ['subject', 'status', 'uploaded_at']
    search_fields = ['uploaded_by__username']
    ordering = ['-uploaded_at']
    readonly_fields = ['uploaded_at', 'processed_at']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('uploaded_by', 'subject', 'file')
        }),
        ('処理状況', {
            'fields': ('status', 'error_message')
        }),
        ('システム情報', {
            'fields': ('uploaded_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AnalyticsData)
class AnalyticsDataAdmin(admin.ModelAdmin):
    list_display = ['data_type', 'scope', 'calculated_at']
    list_filter = ['data_type', 'calculated_at']
    search_fields = ['data_type', 'scope']
    ordering = ['-calculated_at']
    readonly_fields = ['calculated_at']


@admin.register(PDFTemplate)
class PDFTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    ordering = ['name']
    readonly_fields = ['created_at']


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'message_short', 'user', 'created_at']
    list_filter = ['level', 'created_at']
    search_fields = ['message', 'user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def message_short(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_short.short_description = 'メッセージ'
    
    def has_add_permission(self, request):
        return False  # ログは自動生成のみ
