"""
Supabaseのデータ確認スクリプト
"""
from supabase_config import get_supabase_admin_client

def check_supabase_data():
    """Supabaseの全テーブルのデータを確認"""
    print("=== Supabaseデータ確認 ===")
    
    try:
        supabase = get_supabase_admin_client()
        
        # 確認するテーブル
        tables = [
            'accounts_user',
            'quiz_app_subject', 
            'quiz_app_unit',
            'quiz_app_question',
            'quiz_app_quizsession',
            'quiz_app_quizresult'
        ]
        
        total_records = 0
        
        for table in tables:
            try:
                result = supabase.table(table).select('*').execute()
                count = len(result.data)
                print(f"✓ {table}: {count}件")
                total_records += count
            except Exception as e:
                print(f"✗ {table}: エラー - {e}")
        
        print(f"\n合計レコード数: {total_records}件")
        print("✓ Supabase接続は正常です！")
        
        return True
        
    except Exception as e:
        print(f"✗ Supabase接続エラー: {e}")
        return False

if __name__ == '__main__':
    check_supabase_data()
