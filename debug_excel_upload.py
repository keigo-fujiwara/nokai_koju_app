#!/usr/bin/env python
"""
本番環境でのエクセルアップロード問題をデバッグするスクリプト
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

from quiz_app.utils import sync_alternatives_to_supabase
from quiz_app.models import Question, Subject
from django.conf import settings

def check_environment():
    """環境設定の確認"""
    print("🔍 環境設定確認")
    print("=" * 50)
    
    print(f"DEBUG: {settings.DEBUG}")
    print(f"DATABASE ENGINE: {settings.DATABASES['default']['ENGINE']}")
    print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL', '未設定')}")
    print(f"SUPABASE_ANON_KEY: {os.getenv('SUPABASE_ANON_KEY', '未設定')[:20] if os.getenv('SUPABASE_ANON_KEY') else '未設定'}...")
    
    # 本番環境かどうかの判定
    is_production = not settings.DEBUG
    print(f"本番環境: {is_production}")

def test_supabase_connection():
    """Supabase接続テスト"""
    print("\n🔗 Supabase接続テスト")
    print("=" * 50)
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase環境変数が設定されていません")
        return False
    
    try:
        import requests
        
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
        }
        
        # 簡単な接続テスト
        test_url = f"{supabase_url}/rest/v1/quiz_app_question?select=id&limit=1"
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Supabase接続成功")
            return True
        else:
            print(f"❌ Supabase接続失敗: {response.status_code}")
            print(f"レスポンス: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Supabase接続エラー: {e}")
        return False

def test_sync_function():
    """同期関数のテスト"""
    print("\n🔄 同期関数テスト")
    print("=" * 50)
    
    subjects = Subject.objects.all()
    
    for subject in subjects:
        print(f"\n📝 教科: {subject.label_ja} ({subject.code})")
        
        # 問題数を確認
        question_count = Question.objects.filter(unit__subject=subject).count()
        print(f"   問題数: {question_count}")
        
        # 別解がある問題数
        questions_with_alternatives = Question.objects.filter(
            unit__subject=subject,
            accepted_alternatives__isnull=False
        ).exclude(accepted_alternatives=[])
        print(f"   別解がある問題数: {questions_with_alternatives.count()}")
        
        # 同期テスト（最初の5件のみ）
        if questions_with_alternatives.count() > 0:
            print(f"   同期テスト開始...")
            result = sync_alternatives_to_supabase(subject.code)
            
            if result['success']:
                if result.get('skipped'):
                    print(f"   ⚠️ 同期をスキップしました（ローカル環境）")
                else:
                    print(f"   ✅ 同期成功: {result['updated_count']}件更新, {result['failed_count']}件失敗")
                    if result.get('errors'):
                        print(f"   ⚠️ エラー: {len(result['errors'])}件")
            else:
                print(f"   ❌ 同期失敗: {result['error']}")
        else:
            print(f"   ⚠️ 別解がある問題がないためスキップ")

def check_data_consistency():
    """データ整合性チェック"""
    print("\n📊 データ整合性チェック")
    print("=" * 50)
    
    total_questions = Question.objects.count()
    questions_with_alternatives = Question.objects.filter(
        accepted_alternatives__isnull=False
    ).exclude(accepted_alternatives=[])
    
    print(f"総問題数: {total_questions}")
    print(f"別解がある問題数: {questions_with_alternatives.count()}")
    
    # 別解データの形式チェック
    invalid_alternatives = 0
    for question in questions_with_alternatives[:10]:  # 最初の10件のみチェック
        alternatives = question.accepted_alternatives
        if not isinstance(alternatives, list):
            invalid_alternatives += 1
            print(f"⚠️ 問題ID {question.id}: 別解がリスト形式ではありません: {type(alternatives)}")
    
    if invalid_alternatives == 0:
        print("✅ 別解データの形式は正常です")

def main():
    print("🚀 エクセルアップロード問題デバッグ")
    print("=" * 50)
    
    # 環境設定確認
    check_environment()
    
    # Supabase接続テスト
    connection_ok = test_supabase_connection()
    
    # データ整合性チェック
    check_data_consistency()
    
    # 同期関数テスト
    if connection_ok:
        test_sync_function()
    else:
        print("\n⚠️ Supabase接続に問題があるため、同期テストをスキップします")
    
    print("\n🎉 デバッグ完了")
    print("\n📝 推奨事項:")
    if not settings.DEBUG:
        print("1. 本番環境では、Supabase環境変数が正しく設定されているか確認")
        print("2. SupabaseのRLS（Row Level Security）設定を確認")
        print("3. ネットワーク接続とタイムアウト設定を確認")
    else:
        print("1. ローカル環境では、エクセルアップロードはSQLite3に保存されます")
        print("2. 本番環境では、Supabaseとの同期が自動的に実行されます")

if __name__ == '__main__':
    main()
