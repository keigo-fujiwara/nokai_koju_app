#!/usr/bin/env python
"""
Render用データベース移行スクリプト
SQLiteからPostgreSQLへのデータ移行
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
from django.core.management import execute_from_command_line
from accounts.models import User, StudentProfile, AdminProfile
from quiz_app.models import Subject, Unit, Question, QuizSession, QuizAttempt, Homework
from admin_panel.models import AdminUser

def migrate_to_render():
    """Render用PostgreSQLへのデータ移行"""
    print("🚀 Render用データベース移行を開始します...")
    
    try:
        # マイグレーション実行
        print("📦 データベースマイグレーションを実行中...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # 初期データ作成
        print("📝 初期データを作成中...")
        execute_from_command_line(['manage.py', 'create_initial_data'])
        
        print("✅ データベース移行が完了しました！")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False
    
    return True

if __name__ == '__main__':
    migrate_to_render()
