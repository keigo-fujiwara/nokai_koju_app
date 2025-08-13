#!/usr/bin/env python
"""
ローカル環境のデータベース設定を確認するスクリプト
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

from django.conf import settings
from django.db import connection

def main():
    print("🔍 ローカル環境のデータベース設定確認")
    print("=" * 50)
    
    # 環境変数の確認
    print("📋 環境変数:")
    print(f"  - DEBUG: {settings.DEBUG}")
    print(f"  - DATABASE_URL: {os.getenv('DATABASE_URL', '未設定')}")
    
    # データベース設定の確認
    print("\n🗄️ データベース設定:")
    db_config = settings.DATABASES['default']
    print(f"  - ENGINE: {db_config['ENGINE']}")
    print(f"  - NAME: {db_config['NAME']}")
    
    if 'OPTIONS' in db_config:
        print(f"  - OPTIONS: {db_config['OPTIONS']}")
    
    # データベース接続テスト
    print("\n🔗 データベース接続テスト:")
    try:
        with connection.cursor() as cursor:
            if 'sqlite' in db_config['ENGINE']:
                cursor.execute("SELECT sqlite_version();")
                version = cursor.fetchone()
                print(f"  ✅ SQLite接続成功: {version[0]}")
            else:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"  ✅ PostgreSQL接続成功: {version[0]}")
    except Exception as e:
        print(f"  ❌ データベース接続エラー: {e}")
    
    # 現在のデータ確認
    print("\n📊 現在のデータ状況:")
    try:
        from quiz_app.models import Question, Subject, Unit
        from accounts.models import StudentProfile
        
        question_count = Question.objects.count()
        subject_count = Subject.objects.count()
        unit_count = Unit.objects.count()
        student_count = StudentProfile.objects.count()
        
        print(f"  - 問題数: {question_count}")
        print(f"  - 教科数: {subject_count}")
        print(f"  - 単元数: {unit_count}")
        print(f"  - 生徒数: {student_count}")
        
        # 別解がある問題数
        questions_with_alternatives = Question.objects.filter(accepted_alternatives__isnull=False).exclude(accepted_alternatives=[])
        print(f"  - 別解がある問題数: {questions_with_alternatives.count()}")
        
    except Exception as e:
        print(f"  ❌ データ確認エラー: {e}")
    
    print("\n🎯 結論:")
    if 'sqlite' in db_config['ENGINE']:
        print("  ✅ ローカル環境でSQLite3を使用しています")
        print("  📝 エクセルアップロードはSQLite3に保存されます")
    else:
        print("  ⚠️ PostgreSQLを使用しています")
        print("  📝 エクセルアップロードはPostgreSQLに保存されます")

if __name__ == '__main__':
    main()
