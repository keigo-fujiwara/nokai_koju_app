from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, AdminProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['username', 'email']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('追加情報', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('追加情報', {'fields': ('role',)}),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'member_id', 'school', 'class_name', 'grade', 'prefecture']
    list_filter = ['grade', 'prefecture', 'school']
    search_fields = ['nickname', 'member_id', 'school', 'class_name']
    ordering = ['school', 'class_name', 'nickname']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('user', 'member_id', 'nickname')
        }),
        ('学校情報', {
            'fields': ('prefecture', 'school', 'class_name', 'grade')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'employee_number', 'email', 'user']
    list_filter = ['created_at']
    search_fields = ['name', 'employee_number', 'email']
    ordering = ['name']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('user', 'name', 'employee_number', 'email')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
