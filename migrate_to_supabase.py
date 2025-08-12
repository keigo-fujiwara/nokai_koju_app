"""
SQLiteからSupabaseへのデータ移行スクリプト
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from supabase_config import get_supabase_admin_client
import json

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz_app.models import Subject, Unit, Question, QuizSession, QuizAttempt
from accounts.models import User

def migrate_data_to_supabase():
    """SQLiteからSupabaseにデータを移行"""
    print("データ移行を開始します...")
    
    # Supabaseクライアントを取得
    supabase = get_supabase_admin_client()
    
    try:
        # 1. ユーザーデータの移行
        print("ユーザーデータを移行中...")
        users = User.objects.all()
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'user_type': user.role,
                'grade_year': '',
                'school_name': '',
            }
            
            # パスワードハッシュも移行（セキュリティのため）
            if user.password:
                user_data['password'] = user.password
            
            # Supabaseに挿入
            result = supabase.table('accounts_user').upsert(user_data).execute()
            print(f"ユーザー {user.username} を移行しました")
        
        # 2. 教科データの移行
        print("教科データを移行中...")
        subjects = Subject.objects.all()
        for subject in subjects:
            subject_data = {
                'id': subject.id,
                'code': subject.code,
                'label_ja': subject.label_ja,
            }
            supabase.table('quiz_app_subject').upsert(subject_data).execute()
            print(f"教科 {subject.label_ja} を移行しました")
        
        # 3. 単元データの移行
        print("単元データを移行中...")
        units = Unit.objects.all()
        for unit in units:
            unit_data = {
                'id': unit.id,
                'subject_id': unit.subject.id,
                'grade_year': unit.grade_year,
                'category': unit.category,
                'unit_key': unit.unit_key,
            }
            supabase.table('quiz_app_unit').upsert(unit_data).execute()
            print(f"単元 {unit.category} を移行しました")
        
        # 4. 問題データの移行
        print("問題データを移行中...")
        questions = Question.objects.all()
        for question in questions:
            question_data = {
                'id': question.id,
                'unit_id': question.unit.id,
                'source_id': question.source_id,
                'question_type': question.question_type,
                'text': question.text,
                'correct_answer': question.correct_answer,
                'accepted_alternatives': json.dumps(question.accepted_alternatives),
                'choices': json.dumps(question.choices),
                'requires_unit_label': question.requires_unit_label,
                'unit_label_text': question.unit_label_text,
                'explanation': question.explanation,
                'difficulty_level': question.difficulty_level,
                'created_at': question.created_at.isoformat(),
                'updated_at': question.updated_at.isoformat(),
            }
            supabase.table('quiz_app_question').upsert(question_data).execute()
            print(f"問題 {question.id} を移行しました")
        
        # 5. クイズセッションデータの移行
        print("クイズセッションデータを移行中...")
        sessions = QuizSession.objects.all()
        for session in sessions:
            session_data = {
                'id': session.id,
                'user_id': session.user.id,
                'unit_id': session.unit.id,
                'started_at': session.started_at.isoformat(),
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'question_ids': json.dumps(session.question_ids),
                'choice_mappings': json.dumps(session.choice_mappings),
            }
            supabase.table('quiz_app_quizsession').upsert(session_data).execute()
            print(f"クイズセッション {session.id} を移行しました")
        
        # 6. クイズ解答記録データの移行
        print("クイズ解答記録データを移行中...")
        attempts = QuizAttempt.objects.all()
        for attempt in attempts:
            attempt_data = {
                'id': attempt.id,
                'session_id': attempt.session.id,
                'question_id': attempt.question.id,
                'user_answer': attempt.answer_text,
                'is_correct': attempt.is_correct,
                'score': 1 if attempt.is_correct else 0,
                'time_taken': attempt.time_spent_sec,
                'answered_at': attempt.created_at.isoformat(),
            }
            supabase.table('quiz_app_quizresult').upsert(attempt_data).execute()
            print(f"クイズ解答記録 {attempt.id} を移行しました")
        
        print("データ移行が完了しました！")
        
    except Exception as e:
        print(f"データ移行中にエラーが発生しました: {e}")
        raise

if __name__ == '__main__':
    migrate_data_to_supabase()
