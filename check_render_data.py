#!/usr/bin/env python
"""
Renderデータベースの状況確認スクリプト
"""
import os
import sys
import django

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from quiz_app.models import Subject, Unit, Question
from accounts.models import StudentProfile, AdminProfile

def check_database():
    """データベースの状況を確認"""
    print("🔍 Renderデータベースの状況確認")
    print("=" * 50)
    
    try:
        # ユーザー情報
        user_count = User.objects.count()
        print(f"👥 ユーザー数: {user_count}")
        
        if user_count > 0:
            users = User.objects.all()[:5]  # 最初の5人
            for user in users:
                print(f"  - {user.username} ({user.email}) - アクティブ: {user.is_active}")
        
        # プロフィール情報
        student_count = StudentProfile.objects.count()
        admin_count = AdminProfile.objects.count()
        print(f"👨‍🎓 学生プロフィール数: {student_count}")
        print(f"👨‍💼 管理者プロフィール数: {admin_count}")
        
        # 教科・単元・問題情報
        subject_count = Subject.objects.count()
        unit_count = Unit.objects.count()
        question_count = Question.objects.count()
        
        print(f"📚 教科数: {subject_count}")
        print(f"📖 単元数: {unit_count}")
        print(f"❓ 問題数: {question_count}")
        
        if subject_count > 0:
            subjects = Subject.objects.all()
            for subject in subjects:
                print(f"  📚 {subject.name}")
                units = subject.units.all()
                for unit in units:
                    print(f"    📖 {unit.name} (問題数: {unit.questions.count()})")
        
        # データベース接続確認
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print(f"🗄️ データベース: {db_version[0]}")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
