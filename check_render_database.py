#!/usr/bin/env python
"""
Render PostgreSQLデータベース確認スクリプト
"""

import os
import sys
import django
from pathlib import Path

# Django設定を読み込み
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from accounts.models import User, StudentProfile, AdminProfile
from quiz_app.models import Subject, Unit, Question, QuizSession, QuizAttempt, Homework

def check_render_database():
    """Renderデータベースの状況を確認"""
    print("🔍 Render PostgreSQLデータベースの状況を確認中...")
    
    try:
        # データベース接続確認
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ データベース接続成功: {version[0]}")
        
        # 各テーブルのレコード数を確認
        print("\n📊 テーブル別レコード数:")
        print("-" * 40)
        
        # User関連
        user_count = User.objects.count()
        print(f"User: {user_count}件")
        
        student_profile_count = StudentProfile.objects.count()
        print(f"StudentProfile: {student_profile_count}件")
        
        admin_profile_count = AdminProfile.objects.count()
        print(f"AdminProfile: {admin_profile_count}件")
        
        # Quiz関連
        subject_count = Subject.objects.count()
        print(f"Subject: {subject_count}件")
        
        unit_count = Unit.objects.count()
        print(f"Unit: {unit_count}件")
        
        question_count = Question.objects.count()
        print(f"Question: {question_count}件")
        
        quiz_session_count = QuizSession.objects.count()
        print(f"QuizSession: {quiz_session_count}件")
        
        quiz_attempt_count = QuizAttempt.objects.count()
        print(f"QuizAttempt: {quiz_attempt_count}件")
        
        # Admin関連
        homework_count = Homework.objects.count()
        print(f"Homework: {homework_count}件")
        
        print("-" * 40)
        
        if subject_count == 0:
            print("❌ データが存在しません。データ移行が必要です。")
            return False
        else:
            print("✅ データが正常に存在しています。")
            return True
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

if __name__ == '__main__':
    check_render_database()
