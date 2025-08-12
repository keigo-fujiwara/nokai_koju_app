"""
DjangoとSupabaseの接続テスト
"""
import os
import django
from django.conf import settings
from django.db import connection

# 環境変数を読み込み
from dotenv import load_dotenv
load_dotenv()

def test_django_database_connection():
    """Djangoのデータベース接続をテスト"""
    print("=== Djangoデータベース接続テスト ===")
    
    # 環境変数を確認
    database_url = os.getenv('DATABASE_URL')
    print(f"DATABASE_URL: {database_url}")
    
    try:
        # Django設定を読み込み
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        # データベース接続をテスト
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✓ PostgreSQL接続成功: {version[0]}")
        
        # テーブルの存在確認
        tables = [
            'accounts_user',
            'quiz_app_subject',
            'quiz_app_unit',
            'quiz_app_question',
            'quiz_app_quizsession',
            'quiz_app_quizresult'
        ]
        
        for table in tables:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cursor.fetchone()[0]
                    print(f"✓ テーブル {table}: {count}件")
            except Exception as e:
                print(f"✗ テーブル {table}: エラー - {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Djangoデータベース接続エラー: {e}")
        return False

def test_supabase_client():
    """Supabaseクライアントの接続をテスト"""
    print("\n=== Supabaseクライアント接続テスト ===")
    
    try:
        from supabase_config import get_supabase_admin_client
        
        supabase = get_supabase_admin_client()
        
        # 簡単なクエリを実行
        result = supabase.table('quiz_app_subject').select('*').limit(1).execute()
        print(f"✓ Supabaseクライアント接続成功: {len(result.data)}件のデータを取得")
        
        return True
        
    except Exception as e:
        print(f"✗ Supabaseクライアント接続エラー: {e}")
        return False

if __name__ == '__main__':
    print("DjangoとSupabaseの接続テストを開始します...\n")
    
    django_result = test_django_database_connection()
    supabase_result = test_supabase_client()
    
    print("\n" + "="*50)
    print("テスト結果:")
    print(f"Django接続: {'✓ 成功' if django_result else '✗ 失敗'}")
    print(f"Supabase接続: {'✓ 成功' if supabase_result else '✗ 失敗'}")
    
    if django_result and supabase_result:
        print("\n🎉 全ての接続テストが成功しました！")
    else:
        print("\n⚠️  一部の接続テストが失敗しました。")
