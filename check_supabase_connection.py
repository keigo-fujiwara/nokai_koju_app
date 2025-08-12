"""
Supabase接続詳細確認スクリプト
"""
import os
from dotenv import load_dotenv
from supabase_config import get_supabase_admin_client

def check_supabase_connection_details():
    """Supabase接続の詳細を確認"""
    print("=== Supabase接続詳細確認 ===")
    
    # 環境変数を読み込み
    load_dotenv()
    
    # 接続情報を表示（パスワードは一部マスク）
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    database_url = os.getenv('DATABASE_URL')
    
    print(f"✓ Supabase URL: {supabase_url}")
    print(f"✓ Supabase Key: {supabase_key[:20]}..." if supabase_key else "✗ Supabase Key: 未設定")
    print(f"✓ Service Role Key: {service_role_key[:20]}..." if service_role_key else "✗ Service Role Key: 未設定")
    
    if database_url:
        # パスワードをマスク
        masked_url = database_url.replace(database_url.split('@')[0].split(':')[-1], '***')
        print(f"✓ Database URL: {masked_url}")
    else:
        print("✗ Database URL: 未設定")
    
    print("\n=== 接続テスト ===")
    
    try:
        # Supabaseクライアントで接続テスト
        supabase = get_supabase_admin_client()
        
        # 簡単なクエリを実行
        result = supabase.table('quiz_app_subject').select('*').limit(1).execute()
        
        if result.data:
            print("✓ Supabaseクライアント接続: 成功")
            print(f"✓ サンプルデータ: {result.data[0]}")
        else:
            print("⚠️ Supabaseクライアント接続: 成功（データなし）")
            
        return True
        
    except Exception as e:
        print(f"✗ Supabaseクライアント接続エラー: {e}")
        return False

if __name__ == '__main__':
    check_supabase_connection_details()
