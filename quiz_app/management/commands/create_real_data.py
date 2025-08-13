from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from quiz_app.models import Subject, Unit, Question
from accounts.models import StudentProfile, AdminProfile

User = get_user_model()


class Command(BaseCommand):
    help = '実際の学習内容に基づく問題データを作成します'

    def handle(self, *args, **options):
        self.stdout.write('🚀 実際の学習内容に基づく問題データを作成中...')
        
        # 教科データの作成
        subjects = [
            {'code': 'science', 'label_ja': '理科'},
            {'code': 'social', 'label_ja': '社会'},
        ]
        
        for subject_data in subjects:
            subject, created = Subject.objects.get_or_create(
                code=subject_data['code'],
                defaults=subject_data
            )
            if created:
                self.stdout.write(f'✅ 教科を作成: {subject.label_ja}')
            else:
                self.stdout.write(f'📝 教科は既に存在: {subject.label_ja}')
        
        # 単元データの作成
        units_data = [
            # 理科
            {'subject_code': 'science', 'grade_year': '中1', 'category': '化学'},
            {'subject_code': 'science', 'grade_year': '中1', 'category': '生物'},
            {'subject_code': 'science', 'grade_year': '中1', 'category': '物理'},
            {'subject_code': 'science', 'grade_year': '中1', 'category': '地学'},
            {'subject_code': 'science', 'grade_year': '中2', 'category': '化学'},
            {'subject_code': 'science', 'grade_year': '中2', 'category': '生物'},
            {'subject_code': 'science', 'grade_year': '中2', 'category': '物理'},
            {'subject_code': 'science', 'grade_year': '中2', 'category': '地学'},
            {'subject_code': 'science', 'grade_year': '中3', 'category': '化学'},
            {'subject_code': 'science', 'grade_year': '中3', 'category': '生物'},
            {'subject_code': 'science', 'grade_year': '中3', 'category': '物理'},
            {'subject_code': 'science', 'grade_year': '中3', 'category': '地学'},
            {'subject_code': 'science', 'grade_year': '中3', 'category': '自然科学'},
            # 社会
            {'subject_code': 'social', 'grade_year': '中1', 'category': '地理'},
            {'subject_code': 'social', 'grade_year': '中1', 'category': '歴史'},
            {'subject_code': 'social', 'grade_year': '中2', 'category': '地理'},
            {'subject_code': 'social', 'grade_year': '中2', 'category': '歴史'},
            {'subject_code': 'social', 'grade_year': '中3', 'category': '地理'},
            {'subject_code': 'social', 'grade_year': '中3', 'category': '歴史'},
            {'subject_code': 'social', 'grade_year': '中3', 'category': '公民'},
        ]
        
        created_units = []
        for unit_data in units_data:
            subject = Subject.objects.get(code=unit_data['subject_code'])
            unit, created = Unit.objects.get_or_create(
                subject=subject,
                grade_year=unit_data['grade_year'],
                category=unit_data['category']
            )
            if created:
                self.stdout.write(f'✅ 単元を作成: {unit}')
                created_units.append(unit)
            else:
                self.stdout.write(f'📝 単元は既に存在: {unit}')
                created_units.append(unit)
        
        # 実際の学習内容に基づく問題データの作成
        self.stdout.write('📚 実際の学習内容に基づく問題データを作成中...')
        
        # 理科の問題データ
        science_questions = {
            '中1化学': [
                {
                    'text': '物質の三態について正しいのはどれか。',
                    'type': 'choice',
                    'choices': ['固体→液体→気体の順に粒子の運動が激しくなる', '気体→液体→固体の順に粒子の運動が激しくなる', '三態では粒子の運動は変わらない', '三態では粒子の数が変わる'],
                    'correct': '固体→液体→気体の順に粒子の運動が激しくなる'
                },
                {
                    'text': '水の沸点は何度か。',
                    'type': 'text',
                    'correct': '100',
                    'alternatives': ['100度', '100°C']
                },
                {
                    'text': '純粋な物質と混合物の違いを説明しなさい。',
                    'type': 'text',
                    'correct': '純粋な物質は1種類の物質からなり、混合物は2種類以上の物質が混ざったもの',
                    'alternatives': ['純粋な物質は1種類、混合物は複数種類の物質', '純粋な物質は単一成分、混合物は複数成分']
                }
            ],
            '中1生物': [
                {
                    'text': '植物の光合成で必要なものはどれか。',
                    'type': 'choice',
                    'choices': ['光、水、二酸化炭素', '光、水、酸素', '光、二酸化炭素、酸素', '水、二酸化炭素、酸素'],
                    'correct': '光、水、二酸化炭素'
                },
                {
                    'text': '光合成の反応式を書きなさい。',
                    'type': 'text',
                    'correct': '6CO2 + 12H2O → C6H12O6 + 6O2 + 6H2O',
                    'alternatives': ['二酸化炭素+水→ブドウ糖+酸素+水', 'CO2+H2O→C6H12O6+O2+H2O']
                }
            ],
            '中1物理': [
                {
                    'text': '音の三要素は何か。',
                    'type': 'choice',
                    'choices': ['音の大きさ、高さ、音色', '音の速さ、大きさ、高さ', '音の波長、振幅、周波数', '音の強度、周波数、波形'],
                    'correct': '音の大きさ、高さ、音色'
                },
                {
                    'text': '音の速さは空気中で約何m/sか。',
                    'type': 'text',
                    'correct': '340',
                    'alternatives': ['340m/s', '340メートル毎秒']
                }
            ],
            '中1地学': [
                {
                    'text': '地球の内部構造で最も外側にあるのはどれか。',
                    'type': 'choice',
                    'choices': ['地殻', 'マントル', '外核', '内核'],
                    'correct': '地殻'
                },
                {
                    'text': '地震の震源地を求めるために必要な観測点は最低何点か。',
                    'type': 'text',
                    'correct': '3',
                    'alternatives': ['3点', '3箇所']
                }
            ]
        }
        
        # 社会の問題データ
        social_questions = {
            '中1地理': [
                {
                    'text': '日本の都道府県で最も人口が多いのはどこか。',
                    'type': 'choice',
                    'choices': ['東京都', '大阪府', '神奈川県', '愛知県'],
                    'correct': '東京都'
                },
                {
                    'text': '日本の国土面積は約何万平方キロメートルか。',
                    'type': 'text',
                    'correct': '38',
                    'alternatives': ['38万', '38万km²']
                }
            ],
            '中1歴史': [
                {
                    'text': '日本で最初の統一政権を築いたのは誰か。',
                    'type': 'choice',
                    'choices': ['卑弥呼', '聖徳太子', '推古天皇', '天武天皇'],
                    'correct': '卑弥呼'
                },
                {
                    'text': '大化の改新が始まった年を西暦で答えなさい。',
                    'type': 'text',
                    'correct': '645',
                    'alternatives': ['645年', '645年頃']
                }
            ]
        }
        
        # 問題データの作成
        total_questions = 0
        
        for unit in created_units:
            unit_key = f"{unit.grade_year}{unit.category}"
            questions_data = []
            
            # 理科の問題
            if unit.subject.code == 'science' and unit_key in science_questions:
                questions_data = science_questions[unit_key]
            # 社会の問題
            elif unit.subject.code == 'social' and unit_key in social_questions:
                questions_data = social_questions[unit_key]
            
            # 各単元に問題を作成
            for i, q_data in enumerate(questions_data):
                if q_data['type'] == 'text':
                    question = Question.objects.create(
                        unit=unit,
                        source_id=f"{unit.subject.code}_{unit.grade_year}_{unit.category}_{i+1:03d}",
                        question_type='text',
                        text=q_data['text'],
                        correct_answer=q_data['correct'],
                        accepted_alternatives=q_data.get('alternatives', []),
                        requires_unit_label=False,
                        unit_label_text=""
                    )
                else:  # choice
                    question = Question.objects.create(
                        unit=unit,
                        source_id=f"{unit.subject.code}_{unit.grade_year}_{unit.category}_{i+1:03d}",
                        question_type='choice',
                        text=q_data['text'],
                        correct_answer=q_data['correct'],
                        accepted_alternatives=[],
                        choices=q_data['choices'],
                        requires_unit_label=False,
                        unit_label_text=""
                    )
                
                total_questions += 1
                self.stdout.write(f'📝 問題作成: {unit} - {q_data["text"][:30]}...')
        
        # 管理者ユーザーの作成
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
        
        # テスト用生徒ユーザーの作成
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
        
        # 最終統計
        subject_count = Subject.objects.count()
        unit_count = Unit.objects.count()
        question_count = Question.objects.count()
        user_count = User.objects.count()
        
        self.stdout.write(self.style.SUCCESS('🎉 実際の学習内容に基づく問題データの作成が完了しました！'))
        self.stdout.write(f'📊 統計:')
        self.stdout.write(f'  - 教科: {subject_count}件')
        self.stdout.write(f'  - 単元: {unit_count}件')
        self.stdout.write(f'  - 問題: {question_count}件')
        self.stdout.write(f'  - ユーザー: {user_count}件')
