from django.core.management.base import BaseCommand
from quiz_app.models import Question
import json

class Command(BaseCommand):
    help = '問題に別解を追加します'

    def handle(self, *args, **options):
        self.stdout.write('🔧 別解の追加を開始...')
        
        # 別解データの定義
        alternatives_data = {
            # 化学の問題
            719: ['有機化合物'],  # 有機物
            720: ['無機化合物'],  # 無機物
            721: ['合成樹脂', '合成高分子'],  # プラスチック
            722: ['PET'],  # ポリエチレンテレフタラート
            723: ['金属元素'],  # 金属
            
            # 物理の問題
            724: ['電気伝導体'],  # 導体
            725: ['電気絶縁体'],  # 絶縁体
            726: ['半導体'],  # 半導体
            727: ['電流'],  # 電流
            728: ['電圧'],  # 電圧
            
            # 生物の問題
            729: ['細胞核'],  # 核
            730: ['細胞質'],  # 細胞質
            731: ['細胞膜'],  # 細胞膜
            732: ['葉緑体'],  # 葉緑体
            733: ['ミトコンドリア'],  # ミトコンドリア
            
            # 地学の問題
            734: ['地殻'],  # 地殻
            735: ['マントル'],  # マントル
            736: ['外核'],  # 外核
            737: ['内核'],  # 内核
            738: ['プレート'],  # プレート
            
            # 地理の問題
            739: ['都道府県'],  # 都道府県
            740: ['市区町村'],  # 市区町村
            741: ['地方'],  # 地方
            742: ['地域'],  # 地域
            743: ['国'],  # 国
            
            # 歴史の問題
            744: ['古代'],  # 古代
            745: ['中世'],  # 中世
            746: ['近世'],  # 近世
            747: ['近代'],  # 近代
            748: ['現代'],  # 現代
        }
        
        updated_count = 0
        
        for question_id, alternatives in alternatives_data.items():
            try:
                question = Question.objects.get(id=question_id)
                
                # 既存の別解と新しい別解を結合
                existing_alternatives = question.accepted_alternatives
                if isinstance(existing_alternatives, str):
                    # 文字列の場合は空のリストとして扱う
                    existing_alternatives = []
                elif not existing_alternatives:
                    existing_alternatives = []
                
                new_alternatives = list(set(existing_alternatives + alternatives))
                
                # 別解を更新
                question.accepted_alternatives = new_alternatives
                question.save()
                
                updated_count += 1
                self.stdout.write(f'✅ 問題ID {question_id}: 別解を追加 ({", ".join(alternatives)})')
                
            except Question.DoesNotExist:
                self.stdout.write(f'⚠️ 問題ID {question_id} が見つかりません')
            except Exception as e:
                self.stdout.write(f'❌ 問題ID {question_id} の更新エラー: {e}')
        
        self.stdout.write(self.style.SUCCESS(f'🎉 別解追加完了: {updated_count}件の問題を更新しました'))
        
        # 別解がある問題の総数を確認
        questions_with_alternatives = Question.objects.filter(accepted_alternatives__isnull=False).exclude(accepted_alternatives=[])
        self.stdout.write(f'📊 別解がある問題の総数: {questions_with_alternatives.count()}件')
