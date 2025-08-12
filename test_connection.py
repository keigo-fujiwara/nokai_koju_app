"""
Supabase接続を直接テストするスクリプト
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# 環境変数を読み込み
load_dotenv()

def test_supabase_connection():
    """Supabase接続をテスト"""
    print("=== Supabase接続テスト ===")
    
    # 環境変数を取得
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    print(f"URL: {supabase_url}")
    print(f"Key: {supabase_key[:20]}..." if supabase_key else "Key: None")
    
    try:
        # Supabaseクライアントを作成
        supabase = create_client(supabase_url, supabase_key)
        
        # 接続テスト（簡単なクエリを実行）
        result = supabase.table('_dummy_table_').select('*').limit(1).execute()
        print("✓ 接続成功")
        
    except Exception as e:
        print(f"✗ 接続エラー: {e}")
        
        # より詳細なエラー情報を表示
        if "getaddrinfo failed" in str(e):
            print("ネットワーク接続の問題です。以下を確認してください：")
            print("1. インターネット接続")
            print("2. Supabaseプロジェクトのステータス")
            print("3. URLの正確性")
        elif "authentication" in str(e).lower():
            print("認証エラーです。APIキーを確認してください。")
        elif "table" in str(e).lower():
            print("テーブルが存在しません。これは正常です（まだテーブルを作成していないため）。")

def test_database_url():
    """データベースURLをテスト"""
    print("\n=== データベースURLテスト ===")
    
    database_url = os.getenv('DATABASE_URL')
    print(f"Database URL: {database_url}")
    
    if database_url:
        # URLの形式を確認
        if database_url.startswith('postgresql://'):
            print("✓ URL形式は正しい")
        else:
            print("✗ URL形式が正しくありません")
    else:
        print("✗ DATABASE_URLが設定されていません")

if __name__ == '__main__':
    test_supabase_connection()
    test_database_url()
