from django.core.management.base import BaseCommand
from quiz_app.models import Question
import re

class Command(BaseCommand):
    help = '問題データのparts_countフィールドを修正します'

    def handle(self, *args, **options):
        self.stdout.write('🔧 問題データの修正を開始...')
        
        try:
            questions = Question.objects.all()
            fixed_count = 0
            
            for question in questions:
                original_parts_count = question.parts_count
                
                # 問題文から解答欄数を推定
                estimated_parts = self.estimate_parts_count(question.text, question.correct_answer)
                
                # parts_countを更新
                if estimated_parts != original_parts_count:
                    question.parts_count = estimated_parts
                    question.save()
                    fixed_count += 1
                    self.stdout.write(f'✅ 問題ID {question.id}: {original_parts_count} → {estimated_parts}')
            
            self.stdout.write(self.style.SUCCESS(f'🎉 修正完了: {fixed_count}件の問題を修正しました'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ エラーが発生しました: {e}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
    
    def estimate_parts_count(self, text, correct_answer):
        """問題文と正解から解答欄数を推定"""
        
        # 正解に「・」が含まれている場合は複数解答欄
        if '・' in correct_answer:
            return len(correct_answer.split('・'))
        
        # 問題文に「（　）」「（　　）」などの穴埋め表現がある場合
        parentheses_pattern = r'（\s*）'
        matches = re.findall(parentheses_pattern, text)
        if matches:
            return len(matches)
        
        # 問題文に「＿＿＿」などの下線表現がある場合
        underline_pattern = r'＿+'
        matches = re.findall(underline_pattern, text)
        if matches:
            return len(matches)
        
        # デフォルトは1
        return 1
