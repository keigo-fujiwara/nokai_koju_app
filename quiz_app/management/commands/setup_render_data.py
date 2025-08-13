from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from quiz_app.models import Subject, Unit, Question
from accounts.models import StudentProfile, AdminProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Render用の確実なデータセットアップ'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Render用データセットアップを開始...')
        
        try:
            # 1. 教科データの作成
            self.stdout.write('📚 教科データを作成中...')
            science, created = Subject.objects.get_or_create(
                code='science',
                defaults={'label_ja': '理科'}
            )
            if created:
                self.stdout.write('✅ 理科を作成')
            else:
                self.stdout.write('📝 理科は既に存在')
            
            social, created = Subject.objects.get_or_create(
                code='social',
                defaults={'label_ja': '社会'}
            )
            if created:
                self.stdout.write('✅ 社会を作成')
            else:
                self.stdout.write('📝 社会は既に存在')
            
            # 2. 単元データの作成
            self.stdout.write('📖 単元データを作成中...')
            units_data = [
                # 理科
                {'subject': science, 'grade_year': '中1', 'category': '化学'},
                {'subject': science, 'grade_year': '中1', 'category': '生物'},
                {'subject': science, 'grade_year': '中1', 'category': '物理'},
                {'subject': science, 'grade_year': '中1', 'category': '地学'},
                # 社会
                {'subject': social, 'grade_year': '中1', 'category': '地理'},
                {'subject': social, 'grade_year': '中1', 'category': '歴史'},
            ]
            
            created_units = []
            for unit_data in units_data:
                unit, created = Unit.objects.get_or_create(
                    subject=unit_data['subject'],
                    grade_year=unit_data['grade_year'],
                    category=unit_data['category']
                )
                if created:
                    self.stdout.write(f'✅ 単元を作成: {unit}')
                else:
                    self.stdout.write(f'📝 単元は既に存在: {unit}')
                created_units.append(unit)
            
            # 3. 問題データの作成
            self.stdout.write('❓ 問題データを作成中...')
            
            # 理科の問題
            science_questions = [
                {
                    'unit': next(u for u in created_units if u.subject == science and u.category == '化学'),
                    'text': '物質の三態について正しいのはどれか。',
                    'type': 'choice',
                    'choices': ['固体→液体→気体の順に粒子の運動が激しくなる', '気体→液体→固体の順に粒子の運動が激しくなる', '三態では粒子の運動は変わらない', '三態では粒子の数が変わる'],
                    'correct': '固体→液体→気体の順に粒子の運動が激しくなる'
                },
                {
                    'unit': next(u for u in created_units if u.subject == science and u.category == '化学'),
                    'text': '水の沸点は何度か。',
                    'type': 'text',
                    'correct': '100',
                    'alternatives': ['100度', '100°C']
                },
                {
                    'unit': next(u for u in created_units if u.subject == science and u.category == '生物'),
                    'text': '植物の光合成で必要なものはどれか。',
                    'type': 'choice',
                    'choices': ['光、水、二酸化炭素', '光、水、酸素', '光、二酸化炭素、酸素', '水、二酸化炭素、酸素'],
                    'correct': '光、水、二酸化炭素'
                },
                {
                    'unit': next(u for u in created_units if u.subject == science and u.category == '物理'),
                    'text': '音の三要素は何か。',
                    'type': 'choice',
                    'choices': ['音の大きさ、高さ、音色', '音の速さ、大きさ、高さ', '音の波長、振幅、周波数', '音の強度、周波数、波形'],
                    'correct': '音の大きさ、高さ、音色'
                },
                {
                    'unit': next(u for u in created_units if u.subject == science and u.category == '地学'),
                    'text': '地球の内部構造で最も外側にあるのはどれか。',
                    'type': 'choice',
                    'choices': ['地殻', 'マントル', '外核', '内核'],
                    'correct': '地殻'
                }
            ]
            
            # 社会の問題
            social_questions = [
                {
                    'unit': next(u for u in created_units if u.subject == social and u.category == '地理'),
                    'text': '日本の都道府県で最も人口が多いのはどこか。',
                    'type': 'choice',
                    'choices': ['東京都', '大阪府', '神奈川県', '愛知県'],
                    'correct': '東京都'
                },
                {
                    'unit': next(u for u in created_units if u.subject == social and u.category == '歴史'),
                    'text': '日本で最初の統一政権を築いたのは誰か。',
                    'type': 'choice',
                    'choices': ['卑弥呼', '聖徳太子', '推古天皇', '天武天皇'],
                    'correct': '卑弥呼'
                }
            ]
            
            all_questions = science_questions + social_questions
            created_count = 0
            
            for i, q_data in enumerate(all_questions):
                source_id = f"render_{q_data['unit'].subject.code}_{q_data['unit'].grade_year}_{q_data['unit'].category}_{i+1:03d}"
                
                # 既存の問題をチェック
                if Question.objects.filter(unit=q_data['unit'], source_id=source_id).exists():
                    self.stdout.write(f'⏭️ 問題をスキップ: {q_data["text"][:30]}...')
                    continue
                
                if q_data['type'] == 'text':
                    question = Question.objects.create(
                        unit=q_data['unit'],
                        source_id=source_id,
                        question_type='text',
                        text=q_data['text'],
                        correct_answer=q_data['correct'],
                        accepted_alternatives=q_data.get('alternatives', []),
                        requires_unit_label=False,
                        unit_label_text=""
                    )
                else:  # choice
                    question = Question.objects.create(
                        unit=q_data['unit'],
                        source_id=source_id,
                        question_type='choice',
                        text=q_data['text'],
                        correct_answer=q_data['correct'],
                        accepted_alternatives=[],
                        choices=q_data['choices'],
                        requires_unit_label=False,
                        unit_label_text=""
                    )
                
                created_count += 1
                self.stdout.write(f'📝 問題作成: {q_data["text"][:30]}...')
            
            # 4. 管理者ユーザーの作成
            self.stdout.write('👨‍💼 管理者ユーザーを作成中...')
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
            
            # 5. テスト用生徒ユーザーの作成
            self.stdout.write('👨‍🎓 テスト生徒ユーザーを作成中...')
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
            
            # 6. 最終統計
            subject_count = Subject.objects.count()
            unit_count = Unit.objects.count()
            question_count = Question.objects.count()
            user_count = User.objects.count()
            
            self.stdout.write(self.style.SUCCESS('🎉 Render用データセットアップが完了しました！'))
            self.stdout.write(f'📊 統計:')
            self.stdout.write(f'  - 教科: {subject_count}件')
            self.stdout.write(f'  - 単元: {unit_count}件')
            self.stdout.write(f'  - 問題: {question_count}件 (今回作成: {created_count}件)')
            self.stdout.write(f'  - ユーザー: {user_count}件')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ エラーが発生しました: {e}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
        
        self.stdout.write('✅ セットアップ完了')
