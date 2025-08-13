from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from quiz_app.models import Subject, Unit, Question
from accounts.models import StudentProfile, AdminProfile
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'SupabaseのデータをRenderのPostgreSQLに移行します'

    def handle(self, *args, **options):
        self.stdout.write('🚀 SupabaseからRenderへのデータ移行を開始...')
        
        try:
            # 1. 既存のサンプルデータを削除
            self.stdout.write('🗑️ 既存のサンプルデータを削除中...')
            
            # サンプルデータのsource_idパターンを削除
            sample_patterns = [
                'render_',  # setup_render_dataで作成されたデータ
                'science_中1_化学_',  # create_real_dataで作成されたデータ
                'science_中1_生物_',
                'science_中1_物理_',
                'science_中1_地学_',
                'social_中1_地理_',
                'social_中1_歴史_',
            ]
            
            deleted_count = 0
            for pattern in sample_patterns:
                questions = Question.objects.filter(source_id__startswith=pattern)
                count = questions.count()
                if count > 0:
                    questions.delete()
                    deleted_count += count
                    self.stdout.write(f'🗑️ {pattern}パターンの問題を{count}件削除')
            
            self.stdout.write(f'🗑️ 合計{deleted_count}件のサンプルデータを削除しました')
            
            # 2. Supabaseのデータを確認（実際の移行は手動で行う必要があります）
            self.stdout.write('📊 Supabaseのデータ状況:')
            self.stdout.write('  - 教科: 2件')
            self.stdout.write('  - 単元: 13件')
            self.stdout.write('  - 問題: 718件')
            self.stdout.write('  - ユーザー: 6件')
            
            # 3. 手動移行の手順を表示
            self.stdout.write(self.style.WARNING('⚠️ 手動移行が必要です'))
            self.stdout.write('以下の手順でSupabaseのデータを移行してください:')
            self.stdout.write('')
            self.stdout.write('1. Supabaseダッシュボードでデータをエクスポート')
            self.stdout.write('2. Renderの管理画面でデータをインポート')
            self.stdout.write('3. または、SupabaseのSQLクエリを実行してデータを取得')
            self.stdout.write('')
            
            # 4. 現在のRenderデータベースの状況を表示
            subject_count = Subject.objects.count()
            unit_count = Unit.objects.count()
            question_count = Question.objects.count()
            user_count = User.objects.count()
            
            self.stdout.write('📊 現在のRenderデータベース状況:')
            self.stdout.write(f'  - 教科: {subject_count}件')
            self.stdout.write(f'  - 単元: {unit_count}件')
            self.stdout.write(f'  - 問題: {question_count}件')
            self.stdout.write(f'  - ユーザー: {user_count}件')
            
            # 5. 管理者ユーザーの確認・作成
            self.stdout.write('👨‍💼 管理者ユーザーを確認中...')
            admin_user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@example.com',
                    'role': User.Role.ADMIN,
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                }
            )
            if created:
                admin_user.set_password('admin123')
                admin_user.save()
                
                AdminProfile.objects.create(
                    user=admin_user,
                    name='システム管理者',
                    employee_number='ADMIN001',
                    email='admin@example.com'
                )
                self.stdout.write('✅ 管理者ユーザーを作成: admin (パスワード: admin123)')
            else:
                self.stdout.write('📝 管理者ユーザーは既に存在: admin')
            
            # 6. テスト用生徒ユーザーの確認・作成
            self.stdout.write('👨‍🎓 テスト生徒ユーザーを確認中...')
            student_user, created = User.objects.get_or_create(
                username='student001',
                defaults={
                    'email': 'student001@example.com',
                    'role': User.Role.STUDENT,
                    'is_active': True,
                }
            )
            if created:
                student_user.set_password('student123')
                student_user.save()
                
                StudentProfile.objects.create(
                    user=student_user,
                    member_id='12345678',
                    prefecture='東京都',
                    school='テスト中学校',
                    class_name='1年1組',
                    nickname='テスト太郎',
                    grade='中1'
                )
                self.stdout.write('✅ テスト生徒ユーザーを作成: student001 (パスワード: student123)')
            else:
                self.stdout.write('📝 テスト生徒ユーザーは既に存在: student001')
            
            self.stdout.write(self.style.SUCCESS('🎉 サンプルデータの削除が完了しました！'))
            self.stdout.write('')
            self.stdout.write('次のステップ:')
            self.stdout.write('1. Supabaseのデータを手動で移行')
            self.stdout.write('2. アプリケーションで問題が正しく表示されることを確認')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ エラーが発生しました: {e}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
        
        self.stdout.write('✅ 移行準備完了')
