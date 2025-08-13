#!/usr/bin/env python
"""
全角数値の判定テストスクリプト
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

from quiz_app.utils import check_answer, normalize_alphanumeric
from quiz_app.models import Question

def test_normalize_alphanumeric():
    """全角数値の正規化テスト"""
    print("🔍 全角数値正規化テスト")
    print("=" * 50)
    
    test_cases = [
        ("１２３", "123"),
        ("４５６", "456"),
        ("７８９", "789"),
        ("０", "0"),
        ("ＡＢＣ", "ABC"),
        ("ａｂｃ", "abc"),
        ("１２３ＡＢＣ", "123ABC"),
        ("１２３・４５６", "123・456"),
        ("１２３　４５６", "123 456"),
    ]
    
    for input_text, expected in test_cases:
        result = normalize_alphanumeric(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_text}' → '{result}' (期待値: '{expected}')")

def test_answer_checking():
    """回答判定テスト"""
    print("\n🔍 回答判定テスト")
    print("=" * 50)
    
    # 数値問題の例を取得
    numeric_questions = Question.objects.filter(
        correct_answer__regex=r'[０-９]'  # 全角数字を含む問題
    )[:5]
    
    if not numeric_questions:
        print("⚠️ 全角数字を含む問題が見つかりません")
        return
    
    for question in numeric_questions:
        print(f"\n📝 問題ID {question.id}: {question.text[:50]}...")
        print(f"   正解: '{question.correct_answer}'")
        
        # 全角数値での回答テスト
        fullwidth_answer = question.correct_answer
        # 半角数値に変換
        halfwidth_answer = normalize_alphanumeric(question.correct_answer)
        
        # 全角数値で回答した場合のテスト
        is_correct_fullwidth = check_answer(fullwidth_answer, question)
        is_correct_halfwidth = check_answer(halfwidth_answer, question)
        
        print(f"   全角回答 '{fullwidth_answer}' → {'✅ 正解' if is_correct_fullwidth else '❌ 不正解'}")
        print(f"   半角回答 '{halfwidth_answer}' → {'✅ 正解' if is_correct_halfwidth else '❌ 不正解'}")
        
        if not (is_correct_fullwidth and is_correct_halfwidth):
            print(f"   ⚠️ 判定に問題があります")

def test_specific_cases():
    """特定のケースのテスト"""
    print("\n🔍 特定ケースのテスト")
    print("=" * 50)
    
    test_cases = [
        ("１２３", "123"),
        ("４５６", "456"),
        ("７８９", "789"),
        ("１２３・４５６", "123・456"),
        ("ＡＢＣ１２３", "ABC123"),
    ]
    
    for fullwidth, halfwidth in test_cases:
        # 正解が全角の場合
        print(f"\n📝 正解が全角 '{fullwidth}' の場合:")
        print(f"   全角回答 '{fullwidth}' → 正規化後: '{normalize_alphanumeric(fullwidth)}'")
        print(f"   半角回答 '{halfwidth}' → 正規化後: '{normalize_alphanumeric(halfwidth)}'")
        
        # 正解が半角の場合
        print(f"\n📝 正解が半角 '{halfwidth}' の場合:")
        print(f"   全角回答 '{fullwidth}' → 正規化後: '{normalize_alphanumeric(fullwidth)}'")
        print(f"   半角回答 '{halfwidth}' → 正規化後: '{normalize_alphanumeric(halfwidth)}'")

def main():
    print("🚀 全角数値判定テスト")
    print("=" * 50)
    
    # 正規化テスト
    test_normalize_alphanumeric()
    
    # 回答判定テスト
    test_answer_checking()
    
    # 特定ケースのテスト
    test_specific_cases()
    
    print("\n🎉 テスト完了")

if __name__ == '__main__':
    main()
