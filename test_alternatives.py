import os
import django

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz_app.models import Question
from quiz_app.utils import check_answer

print("=== 別解の採点テスト ===")

# 別解がある問題をテスト
test_cases = [
    {
        'question_id': 719,
        'correct_answer': '有機物',
        'alternatives': ['有機化合物'],
        'test_answers': ['有機物', '有機化合物', '無機物', 'プラスチック']
    },
    {
        'question_id': 720,
        'correct_answer': '無機物',
        'alternatives': ['無機化合物'],
        'test_answers': ['無機物', '無機化合物', '有機物', '金属']
    },
    {
        'question_id': 721,
        'correct_answer': 'プラスチック',
        'alternatives': ['合成高分子', '合成樹脂'],
        'test_answers': ['プラスチック', '合成高分子', '合成樹脂', '金属']
    },
    {
        'question_id': 722,
        'correct_answer': 'ポリエチレンテレフタラート',
        'alternatives': ['PET'],
        'test_answers': ['ポリエチレンテレフタラート', 'PET', 'プラスチック', 'ポリエチレン']
    },
    {
        'question_id': 723,
        'correct_answer': '金属',
        'alternatives': ['金属元素'],
        'test_answers': ['金属', '金属元素', 'プラスチック', 'ガラス']
    }
]

for test_case in test_cases:
    try:
        question = Question.objects.get(id=test_case['question_id'])
        print(f"\n--- 問題ID {test_case['question_id']} ---")
        print(f"正解: {test_case['correct_answer']}")
        print(f"別解: {test_case['alternatives']}")
        
        for test_answer in test_case['test_answers']:
            is_correct = check_answer(test_answer, question)
            status = "✅ 正解" if is_correct else "❌ 不正解"
            print(f"  回答: '{test_answer}' → {status}")
            
    except Question.DoesNotExist:
        print(f"⚠️ 問題ID {test_case['question_id']} が見つかりません")

print("\n=== 別解がある問題の総数確認 ===")
questions_with_alternatives = Question.objects.filter(accepted_alternatives__isnull=False).exclude(accepted_alternatives=[])
print(f"別解がある問題数: {questions_with_alternatives.count()}件")

# 別解がある問題の例を表示
print("\n=== 別解がある問題の例 ===")
for question in questions_with_alternatives[:3]:
    print(f"ID: {question.id}")
    print(f"正解: {question.correct_answer}")
    print(f"別解: {question.accepted_alternatives}")
    print()
