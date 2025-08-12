"""
Supabase接続とデータベース操作のテストスクリプト
"""
import os
import django
from django.conf import settings
from supabase_config import get_supabase_client, get_supabase_admin_client
import json

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_supabase_connection():
    """Supabase接続をテスト"""
    print("=== Supabase接続テスト ===")
    
    try:
        # 通常のクライアントで接続テスト
        supabase = get_supabase_client()
        print("✓ 通常クライアント接続成功")
        
        # 管理者クライアントで接続テスト
        admin_supabase = get_supabase_admin_client()
        print("✓ 管理者クライアント接続成功")
        
        return True
    except Exception as e:
        print(f"✗ 接続エラー: {e}")
        return False

def test_table_access():
    """テーブルアクセステスト"""
    print("\n=== テーブルアクセステスト ===")
    
    try:
        supabase = get_supabase_admin_client()
        
        # 各テーブルの存在確認
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
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"✓ テーブル {table} アクセス成功")
            except Exception as e:
                print(f"✗ テーブル {table} アクセス失敗: {e}")
        
        return True
    except Exception as e:
        print(f"✗ テーブルアクセステストエラー: {e}")
        return False

def test_data_operations():
    """データ操作テスト"""
    print("\n=== データ操作テスト ===")
    
    try:
        supabase = get_supabase_admin_client()
        
        # 1. テストデータの挿入
        print("テストデータを挿入中...")
        test_subject = {
            'code': 'test',
            'label_ja': 'テスト理科'
        }
        
        result = supabase.table('quiz_app_subject').insert(test_subject).execute()
        print("✓ テストデータ挿入成功")
        
        # 2. データの取得
        print("データを取得中...")
        result = supabase.table('quiz_app_subject').select('*').eq('code', 'test_science').execute()
        if result.data:
            print("✓ データ取得成功")
            print(f"取得したデータ: {result.data[0]}")
        
        # 3. データの更新
        print("データを更新中...")
        update_data = {'label_ja': '更新されたテスト理科'}
        result = supabase.table('quiz_app_subject').update(update_data).eq('code', 'test_science').execute()
        print("✓ データ更新成功")
        
        # 4. データの削除
        print("テストデータを削除中...")
        result = supabase.table('quiz_app_subject').delete().eq('code', 'test_science').execute()
        print("✓ データ削除成功")
        
        return True
    except Exception as e:
        print(f"✗ データ操作テストエラー: {e}")
        return False

def test_django_models():
    """DjangoモデルとSupabaseの連携テスト"""
    print("\n=== Djangoモデル連携テスト ===")
    
    try:
        from quiz_app.models import Subject, Unit, Question
        from accounts.models import User
        
        # 現在のデータ数を確認
        subject_count = Subject.objects.count()
        unit_count = Unit.objects.count()
        question_count = Question.objects.count()
        user_count = User.objects.count()
        
        print(f"現在のデータ数:")
        print(f"  教科: {subject_count}")
        print(f"  単元: {unit_count}")
        print(f"  問題: {question_count}")
        print(f"  ユーザー: {user_count}")
        
        # 最初の教科データを取得してテスト
        if subject_count > 0:
            first_subject = Subject.objects.first()
            print(f"✓ 最初の教科: {first_subject}")
            
            # 関連する単元を取得
            units = first_subject.units.all()
            print(f"✓ 関連単元数: {units.count()}")
        
        return True
    except Exception as e:
        print(f"✗ Djangoモデルテストエラー: {e}")
        return False

def run_all_tests():
    """全てのテストを実行"""
    print("Supabase接続とデータベース操作のテストを開始します...\n")
    
    tests = [
        ("接続テスト", test_supabase_connection),
        ("テーブルアクセステスト", test_table_access),
        ("データ操作テスト", test_data_operations),
        ("Djangoモデル連携テスト", test_django_models),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name}でエラーが発生: {e}")
            results.append((test_name, False))
    
    # 結果サマリー
    print("\n" + "="*50)
    print("テスト結果サマリー:")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✓ 成功" if result else "✗ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n合計: {passed}/{len(results)} テストが成功")
    
    if passed == len(results):
        print("🎉 全てのテストが成功しました！")
    else:
        print("⚠️  一部のテストが失敗しました。設定を確認してください。")

if __name__ == '__main__':
    run_all_tests()
