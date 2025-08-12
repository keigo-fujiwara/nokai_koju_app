"""
SQLiteを使用してDjangoアプリケーションをテスト
"""
import os
import django
from django.conf import settings

# 一時的にSQLiteを使用
os.environ['DATABASE_URL'] = ''

def test_django_with_sqlite():
    """SQLiteを使用してDjangoをテスト"""
    print("=== SQLiteを使用したDjangoテスト ===")
    
    try:
        # Django設定を読み込み
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        # データベース接続をテスト
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()
            print(f"✓ SQLite接続成功: {version[0]}")
        
        # モデルのテスト
        from quiz_app.models import Subject, Unit, Question
        from accounts.models import User
        
        print(f"✓ ユーザー数: {User.objects.count()}")
        print(f"✓ 教科数: {Subject.objects.count()}")
        print(f"✓ 単元数: {Unit.objects.count()}")
        print(f"✓ 問題数: {Question.objects.count()}")
        
        return True
        
    except Exception as e:
        print(f"✗ SQLiteテストエラー: {e}")
        return False

def test_supabase_data():
    """Supabaseのデータを確認"""
    print("\n=== Supabaseデータ確認 ===")
    
    try:
        from supabase_config import get_supabase_admin_client
        
        supabase = get_supabase_admin_client()
        
        # 各テーブルのデータ数を確認
        tables = [
            'accounts_user',
            'quiz_app_subject',
            'quiz_app_unit',
            'quiz_app_question',
            'quiz_app_quizsession',
            'quiz_app_quizresult'
        ]
        
        for table in tables:
            result = supabase.table(table).select('*', count='exact').execute()
            print(f"✓ {table}: {result.count}件")
        
        return True
        
    except Exception as e:
        print(f"✗ Supabaseデータ確認エラー: {e}")
        return False

if __name__ == '__main__':
    print("Djangoアプリケーションのテストを開始します...\n")
    
    sqlite_result = test_django_with_sqlite()
    supabase_result = test_supabase_data()
    
    print("\n" + "="*50)
    print("テスト結果:")
    print(f"SQLite接続: {'✓ 成功' if sqlite_result else '✗ 失敗'}")
    print(f"Supabaseデータ: {'✓ 成功' if supabase_result else '✗ 失敗'}")
    
    if sqlite_result and supabase_result:
        print("\n🎉 アプリケーションは正常に動作します！")
        print("PostgreSQL接続の問題を解決すれば、Supabaseを使用できます。")
    else:
        print("\n⚠️  アプリケーションに問題があります。")
