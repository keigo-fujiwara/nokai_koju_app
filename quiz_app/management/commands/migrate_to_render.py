from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from quiz_app.models import Subject, Unit, Question
from accounts.models import User, StudentProfile, AdminProfile

class Command(BaseCommand):
    help = 'SQLiteからRender PostgreSQLへのデータ移行'

    def handle(self, *args, **options):
        self.stdout.write("🚀 データ移行を開始します...")
        
        try:
            # 1. マイグレーション実行
            self.stdout.write("📦 マイグレーションを実行中...")
            call_command('migrate')
            
            # 2. 初期データ作成
            self.stdout.write("📝 初期データを作成中...")
            call_command('create_initial_data')
            
            # 3. データ確認
            self.stdout.write("🔍 データ確認中...")
            subject_count = Subject.objects.count()
            unit_count = Unit.objects.count()
            question_count = Question.objects.count()
            user_count = User.objects.count()
            
            self.stdout.write(f"✅ 移行完了:")
            self.stdout.write(f"  - 教科: {subject_count}件")
            self.stdout.write(f"  - 単元: {unit_count}件")
            self.stdout.write(f"  - 問題: {question_count}件")
            self.stdout.write(f"  - ユーザー: {user_count}件")
            
            # 4. 詳細確認
            if subject_count > 0:
                self.stdout.write("📚 教科詳細:")
                for subject in Subject.objects.all():
                    self.stdout.write(f"  - {subject.name}")
                    for unit in subject.units.all():
                        self.stdout.write(f"    📖 {unit.name} (問題数: {unit.questions.count()})")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ エラーが発生しました: {e}"))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
            return False
        
        return True
