#!/usr/bin/env python
"""
SQLiteからRender PostgreSQLへのデータ移行スクリプト
"""

import os
import sys
import django
from pathlib import Path
import json

# Django設定を読み込み
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line
from accounts.models import User, StudentProfile, AdminProfile
from quiz_app.models import Subject, Unit, Question, QuizSession, QuizAttempt, Homework

def export_sqlite_data():
    """SQLiteデータをエクスポート"""
    print("📤 SQLiteデータをエクスポート中...")
    
    # 一時的にSQLiteを使用
    os.environ['DATABASE_URL'] = ''
    
    data = {}
    
    try:
        # User関連データ
        users = User.objects.all()
        data['users'] = []
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'password': user.password,
                'role': user.role,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat(),
            }
            data['users'].append(user_data)
        
        # StudentProfile関連データ
        student_profiles = StudentProfile.objects.all()
        data['student_profiles'] = []
        for profile in student_profiles:
            profile_data = {
                'id': profile.id,
                'user_id': profile.user.id,
                'member_id': profile.member_id,
                'prefecture': profile.prefecture,
                'school': profile.school,
                'class_name': profile.class_name,
                'nickname': profile.nickname,
                'grade': profile.grade,
            }
            data['student_profiles'].append(profile_data)
        
        # AdminProfile関連データ
        admin_profiles = AdminProfile.objects.all()
        data['admin_profiles'] = []
        for profile in admin_profiles:
            profile_data = {
                'id': profile.id,
                'user_id': profile.user.id,
                'name': profile.name,
                'employee_number': profile.employee_number,
                'email': profile.email,
            }
            data['admin_profiles'].append(profile_data)
        
        # Subject関連データ
        subjects = Subject.objects.all()
        data['subjects'] = []
        for subject in subjects:
            subject_data = {
                'id': subject.id,
                'name': subject.name,
                'description': subject.description,
            }
            data['subjects'].append(subject_data)
        
        # Unit関連データ
        units = Unit.objects.all()
        data['units'] = []
        for unit in units:
            unit_data = {
                'id': unit.id,
                'subject_id': unit.subject.id,
                'name': unit.name,
                'description': unit.description,
                'grade_year': unit.grade_year,
                'category': unit.category,
            }
            data['units'].append(unit_data)
        
        # Question関連データ
        questions = Question.objects.all()
        data['questions'] = []
        for question in questions:
            question_data = {
                'id': question.id,
                'unit_id': question.unit.id,
                'text': question.text,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'question_type': question.question_type,
                'choices': question.choices,
                'parts_count': question.parts_count,
            }
            data['questions'].append(question_data)
        
        # データをJSONファイルに保存
        with open('sqlite_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ データエクスポート完了: {len(data['users'])}ユーザー, {len(data['subjects'])}教科, {len(data['questions'])}問題")
        return True
        
    except Exception as e:
        print(f"❌ エクスポートエラー: {e}")
        return False

def import_to_render():
    """Render PostgreSQLにデータをインポート"""
    print("📥 Render PostgreSQLにデータをインポート中...")
    
    try:
        # JSONファイルを読み込み
        with open('sqlite_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Userデータをインポート
        print("👥 ユーザーデータをインポート中...")
        for user_data in data['users']:
            user, created = User.objects.get_or_create(
                id=user_data['id'],
                defaults={
                    'username': user_data['username'],
                    'email': user_data['email'],
                    'password': user_data['password'],
                    'role': user_data['role'],
                    'is_active': user_data['is_active'],
                    'date_joined': user_data['date_joined'],
                }
            )
            if created:
                print(f"  ✅ ユーザー作成: {user.username}")
        
        # StudentProfileデータをインポート
        print("👨‍🎓 生徒プロファイルをインポート中...")
        for profile_data in data['student_profiles']:
            user = User.objects.get(id=profile_data['user_id'])
            profile, created = StudentProfile.objects.get_or_create(
                id=profile_data['id'],
                defaults={
                    'user': user,
                    'member_id': profile_data['member_id'],
                    'prefecture': profile_data['prefecture'],
                    'school': profile_data['school'],
                    'class_name': profile_data['class_name'],
                    'nickname': profile_data['nickname'],
                    'grade': profile_data['grade'],
                }
            )
            if created:
                print(f"  ✅ 生徒プロファイル作成: {profile.nickname}")
        
        # AdminProfileデータをインポート
        print("👨‍💼 管理者プロファイルをインポート中...")
        for profile_data in data['admin_profiles']:
            user = User.objects.get(id=profile_data['user_id'])
            profile, created = AdminProfile.objects.get_or_create(
                id=profile_data['id'],
                defaults={
                    'user': user,
                    'name': profile_data['name'],
                    'employee_number': profile_data['employee_number'],
                    'email': profile_data['email'],
                }
            )
            if created:
                print(f"  ✅ 管理者プロファイル作成: {profile.name}")
        
        # Subjectデータをインポート
        print("📚 教科データをインポート中...")
        for subject_data in data['subjects']:
            subject, created = Subject.objects.get_or_create(
                id=subject_data['id'],
                defaults={
                    'name': subject_data['name'],
                    'description': subject_data['description'],
                }
            )
            if created:
                print(f"  ✅ 教科作成: {subject.name}")
        
        # Unitデータをインポート
        print("📖 単元データをインポート中...")
        for unit_data in data['units']:
            subject = Subject.objects.get(id=unit_data['subject_id'])
            unit, created = Unit.objects.get_or_create(
                id=unit_data['id'],
                defaults={
                    'subject': subject,
                    'name': unit_data['name'],
                    'description': unit_data['description'],
                    'grade_year': unit_data['grade_year'],
                    'category': unit_data['category'],
                }
            )
            if created:
                print(f"  ✅ 単元作成: {unit.name}")
        
        # Questionデータをインポート
        print("❓ 問題データをインポート中...")
        for question_data in data['questions']:
            unit = Unit.objects.get(id=question_data['unit_id'])
            question, created = Question.objects.get_or_create(
                id=question_data['id'],
                defaults={
                    'unit': unit,
                    'text': question_data['text'],
                    'correct_answer': question_data['correct_answer'],
                    'explanation': question_data['explanation'],
                    'question_type': question_data['question_type'],
                    'choices': question_data['choices'],
                    'parts_count': question_data['parts_count'],
                }
            )
            if created:
                print(f"  ✅ 問題作成: {question.text[:30]}...")
        
        print("✅ データインポート完了！")
        return True
        
    except Exception as e:
        print(f"❌ インポートエラー: {e}")
        return False

def migrate_sqlite_to_render():
    """SQLiteからRenderへの完全移行"""
    print("🚀 SQLiteからRender PostgreSQLへのデータ移行を開始します...")
    
    # 1. SQLiteデータをエクスポート
    if not export_sqlite_data():
        print("❌ エクスポートに失敗しました。")
        return False
    
    # 2. Render PostgreSQLにインポート
    if not import_to_render():
        print("❌ インポートに失敗しました。")
        return False
    
    print("🎉 データ移行が完了しました！")
    return True

if __name__ == '__main__':
    migrate_sqlite_to_render()
