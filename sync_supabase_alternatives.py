#!/usr/bin/env python
"""
Supabaseの別解データを手動で同期するスクリプト
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
from quiz_app.models import Question
from accounts.models import StudentProfile

def main():
    print("🔄 Supabase別解データ同期スクリプト")
    print("=" * 50)
    
    # 現在の状況を確認
    print("📊 現在の状況:")
    total_questions = Question.objects.count()
    questions_with_alternatives = Question.objects.filter(accepted_alternatives__isnull=False).exclude(accepted_alternatives=[])
    print(f"  - 総問題数: {total_questions}")
    print(f"  - 別解がある問題数: {questions_with_alternatives.count()}")
    
    # 別解がある問題の例を表示
    print("\n📝 別解がある問題の例:")
    for i, question in enumerate(questions_with_alternatives[:5]):
        alternatives = question.accepted_alternatives
        if isinstance(alternatives, str):
            try:
                import json
                alternatives = json.loads(alternatives)
            except:
                alternatives = []
        print(f"  {i+1}. 問題ID {question.id}: {question.text[:50]}...")
        print(f"     正解: {question.correct_answer}")
        print(f"     別解: {alternatives}")
        print()
    
    # 教科別に同期
    subjects = ['science', 'social']
    
    for subject_code in subjects:
        print(f"\n🔄 {subject_code} の同期を開始...")
        result = sync_alternatives_to_supabase(subject_code)
        
        if result['success']:
            print(f"✅ {subject_code} 同期完了:")
            print(f"  - 成功: {result['updated_count']}件")
            print(f"  - 失敗: {result['failed_count']}件")
            
            if result.get('errors'):
                print(f"  - エラー: {len(result['errors'])}件")
        else:
            print(f"❌ {subject_code} 同期失敗: {result['error']}")
    
    print("\n🎉 同期処理完了")
    
    # 最終確認
    print("\n📊 最終確認:")
    print("Supabaseの別解データを確認してください:")
    print("python check_supabase_alternatives.py")

if __name__ == '__main__':
    main()
