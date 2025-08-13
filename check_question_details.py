import os
import django

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz_app.models import Question

print("=== 問題データの詳細確認 ===")

# 最初の5問の詳細を表示
questions = Question.objects.all()[:5]

for i, question in enumerate(questions, 1):
    print(f"\n--- 問題 {i} ---")
    print(f"ID: {question.id}")
    print(f"問題文: {question.text[:100]}...")
    print(f"正解: {question.correct_answer}")
    print(f"別解: {question.accepted_alternatives}")
    print(f"選択肢: {question.choices}")
    print(f"問題タイプ: {question.question_type}")
    print(f"parts_count: {question.parts_count}")
    print(f"source_id: {question.source_id}")

print(f"\n=== 総問題数: {Question.objects.count()} ===")
