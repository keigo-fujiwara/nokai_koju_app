import re
import json
import unicodedata
from typing import List, Dict, Any, Tuple
from openpyxl import load_workbook
from django.db import transaction
from .models import Subject, Unit, Question


def normalize_alphanumeric(text: str) -> str:
    """
    英数字の半角・全角を正規化する
    """
    if not text:
        return text
    
    # 全角英数字を半角に変換
    normalized = unicodedata.normalize('NFKC', text)
    
    # 全角英数字のマッピング
    fullwidth_to_halfwidth = {
        '０': '0', '１': '1', '２': '2', '３': '3', '４': '4',
        '５': '5', '６': '6', '７': '7', '８': '8', '９': '9',
        'Ａ': 'A', 'Ｂ': 'B', 'Ｃ': 'C', 'Ｄ': 'D', 'Ｅ': 'E',
        'Ｆ': 'F', 'Ｇ': 'G', 'Ｈ': 'H', 'Ｉ': 'I', 'Ｊ': 'J',
        'Ｋ': 'K', 'Ｌ': 'L', 'Ｍ': 'M', 'Ｎ': 'N', 'Ｏ': 'O',
        'Ｐ': 'P', 'Ｑ': 'Q', 'Ｒ': 'R', 'Ｓ': 'S', 'Ｔ': 'T',
        'Ｕ': 'U', 'Ｖ': 'V', 'Ｗ': 'W', 'Ｘ': 'X', 'Ｙ': 'Y',
        'Ｚ': 'Z',
        'ａ': 'a', 'ｂ': 'b', 'ｃ': 'c', 'ｄ': 'd', 'ｅ': 'e',
        'ｆ': 'f', 'ｇ': 'g', 'ｈ': 'h', 'ｉ': 'i', 'ｊ': 'j',
        'ｋ': 'k', 'ｌ': 'l', 'ｍ': 'm', 'ｎ': 'n', 'ｏ': 'o',
        'ｐ': 'p', 'ｑ': 'q', 'ｒ': 'r', 'ｓ': 's', 'ｔ': 't',
        'ｕ': 'u', 'ｖ': 'v', 'ｗ': 'w', 'ｘ': 'x', 'ｙ': 'y',
        'ｚ': 'z'
    }
    
    # 全角英数字を半角に変換
    for full, half in fullwidth_to_halfwidth.items():
        normalized = normalized.replace(full, half)
    
    return normalized


def normalize_text(text: str) -> str:
    """テキストを正規化する"""
    if not text:
        return ""
    
    # 英数字の半角・全角を正規化
    text = normalize_alphanumeric(text)
    
    # 全角・半角の統一
    text = text.replace('　', ' ')  # 全角スペースを半角に
    text = text.replace('（', '(').replace('）', ')')  # 全角括弧を半角に
    text = text.replace('［', '[').replace('］', ']')  # 全角角括弧を半角に
    
    # ひらがな・カタカナの統一（カタカナに統一）
    text = text.replace('ぁ', 'ァ').replace('ぃ', 'ィ').replace('ぅ', 'ゥ').replace('ぇ', 'ェ').replace('ぉ', 'ォ')
    text = text.replace('ゃ', 'ャ').replace('ゅ', 'ュ').replace('ょ', 'ョ')
    text = text.replace('っ', 'ッ')
    text = text.replace('あ', 'ア').replace('い', 'イ').replace('う', 'ウ').replace('え', 'エ').replace('お', 'オ')
    text = text.replace('か', 'カ').replace('き', 'キ').replace('く', 'ク').replace('け', 'ケ').replace('こ', 'コ')
    text = text.replace('さ', 'サ').replace('し', 'シ').replace('す', 'ス').replace('せ', 'セ').replace('そ', 'ソ')
    text = text.replace('た', 'タ').replace('ち', 'チ').replace('つ', 'ツ').replace('て', 'テ').replace('と', 'ト')
    text = text.replace('な', 'ナ').replace('に', 'ニ').replace('ぬ', 'ヌ').replace('ね', 'ネ').replace('の', 'ノ')
    text = text.replace('は', 'ハ').replace('ひ', 'ヒ').replace('ふ', 'フ').replace('へ', 'ヘ').replace('ほ', 'ホ')
    text = text.replace('ま', 'マ').replace('み', 'ミ').replace('む', 'ム').replace('め', 'メ').replace('も', 'モ')
    text = text.replace('や', 'ヤ').replace('ゆ', 'ユ').replace('よ', 'ヨ')
    text = text.replace('ら', 'ラ').replace('り', 'リ').replace('る', 'ル').replace('れ', 'レ').replace('ろ', 'ロ')
    text = text.replace('わ', 'ワ').replace('を', 'ヲ').replace('ん', 'ン')
    
    # 前後の空白を削除
    text = text.strip()
    
    return text


def split_parts(answer: str) -> List[str]:
    """解答を「・」で分割する"""
    if not answer:
        return []
    
    parts = [part.strip() for part in answer.split('・')]
    return [part for part in parts if part]


def parse_alternatives(alternatives_text: str) -> List[str]:
    """別解テキストを解析して配列に変換"""
    if not alternatives_text:
        return []
    
    # 区切り文字で分割（/,、;など）
    alternatives = re.split(r'[/,、;；]', alternatives_text)
    return [normalize_text(alt.strip()) for alt in alternatives if alt.strip()]


def extract_unit_info(unit_text: str) -> Tuple[str, str]:
    """単元テキストから学年とカテゴリを抽出"""
    # 例: "中1化学" -> ("中1", "化学")
    # 全角数字も対応
    grade_match = re.search(r'(中[1-3１２３])', unit_text)
    if grade_match:
        grade = grade_match.group(1)
        # 全角数字を半角に変換
        grade = grade.replace('１', '1').replace('２', '2').replace('３', '3')
    else:
        grade = ""
    
    # 学年部分を除いた残りがカテゴリ
    category = unit_text.replace(grade_match.group(1) if grade_match else "", "").strip()
    
    return grade, category


def check_answer(user_answer: str, question: Question) -> bool:
    """採点ロジック"""
    user_answer = normalize_text(user_answer)
    correct_answer = normalize_text(question.correct_answer)
    
    # 選択問題の場合
    if question.question_type == 'choice':
        # 選択肢のインデックスまたは選択肢のテキストで判定
        try:
            # 数字の場合は選択肢のインデックスとして扱う
            choice_index = int(user_answer) - 1  # 1ベースから0ベースに変換
            if 0 <= choice_index < len(question.choices):
                selected_choice = normalize_text(question.choices[choice_index])
                return selected_choice == correct_answer
        except ValueError:
            # 数字でない場合は直接テキスト比較
            pass
    
    # 基本的な一致チェック
    if user_answer == correct_answer:
        return True
    
    # 別解チェック
    for alternative in question.accepted_alternatives:
        if normalize_text(alternative) == user_answer:
            return True
    
    # 複数解答欄の場合
    if question.parts_count > 1:
        user_parts = split_parts(user_answer)
        correct_parts = split_parts(correct_answer)
        
        if len(user_parts) == len(correct_parts):
            # 順不同でチェック
            user_parts_set = set(user_parts)
            correct_parts_set = set(correct_parts)
            
            if user_parts_set == correct_parts_set:
                return True
    
    return False


def process_xlsm_file(file_path: str, subject_code: str) -> Dict[str, Any]:
    """XLSMファイルを処理してデータを抽出"""
    try:
        workbook = load_workbook(file_path, keep_vba=True)
        worksheet = workbook.active
        
        data = []
        errors = []
        
        # ヘッダー行をスキップ（2行目から開始）
        for row_num, row in enumerate(worksheet.iter_rows(min_row=2, values_only=True), start=2):
            if not row[0]:  # IDが空の行はスキップ
                continue
            
            try:
                # 新しい列の定義: ID, 単元, 問題, 正解, 別解, 問題タイプ, 選択肢1-6, 単位
                source_id = str(row[0]).strip()
                unit_text = str(row[1]).strip()
                question_text = str(row[2]).strip()
                correct_answer = str(row[3]).strip()
                alternatives_text = str(row[4]).strip() if row[4] else ""
                question_type = str(row[5]).strip() if len(row) > 5 and row[5] else "text"
                unit_label_text = str(row[12]).strip() if len(row) > 12 and row[12] else ""
                
                # 問題タイプの正規化
                if question_type.lower() in ['choice', '選択', '選択問題']:
                    question_type = 'choice'
                else:
                    question_type = 'text'
                
                # 選択肢の取得（G列〜L列）
                choices = []
                if question_type == 'choice':
                    # 正解を選択肢に追加
                    choices.append(correct_answer)
                    
                    # 入力された選択肢を追加
                    for i in range(6, 12):  # G列〜L列
                        if len(row) > i and row[i]:
                            choice = str(row[i]).strip()
                            if choice and choice != correct_answer:  # 重複を避ける
                                choices.append(choice)
                    
                    # 選択肢をランダムに並べ替え
                    import random
                    random.shuffle(choices)
                
                # 必須項目のチェック
                if not all([source_id, unit_text, question_text, correct_answer]):
                    errors.append(f"行{row_num}: 必須項目が不足しています")
                    continue
                
                # 単元情報の抽出
                grade, category = extract_unit_info(unit_text)
                if not grade or not category:
                    errors.append(f"行{row_num}: 単元情報の解析に失敗しました: {unit_text}")
                    continue
                
                # 別解の解析
                alternatives = parse_alternatives(alternatives_text)
                
                # 複数解答欄の判定
                parts_count = 1
                if '・' in correct_answer:
                    parts_count = len(split_parts(correct_answer))
                
                # 単位ラベルの判定
                requires_unit_label = bool(unit_label_text)
                if not unit_label_text:
                    # 単位フィールドが空の場合、問題文から自動抽出を試行
                    if any(unit in question_text.lower() for unit in ['g', 'kg', 'm', 'cm', 'l', 'ml']):
                        requires_unit_label = True
                        # 単位の抽出（簡易版）
                        unit_match = re.search(r'([0-9]+)\s*(g|kg|m|cm|l|ml)', question_text)
                        if unit_match:
                            unit_label_text = unit_match.group(2)
                
                data.append({
                    'source_id': source_id,
                    'unit_text': unit_text,
                    'grade': grade,
                    'category': category,
                    'question_text': question_text,
                    'correct_answer': correct_answer,
                    'alternatives': alternatives,
                    'question_type': question_type,
                    'choices': choices,
                    'parts_count': parts_count,
                    'requires_unit_label': requires_unit_label,
                    'unit_label_text': unit_label_text,
                })
                
            except Exception as e:
                errors.append(f"行{row_num}: 処理エラー - {str(e)}")
        
        return {
            'data': data,
            'errors': errors,
            'total_rows': len(data),
            'error_count': len(errors)
        }
        
    except Exception as e:
        return {
            'data': [],
            'errors': [f"ファイル読み込みエラー: {str(e)}"],
            'total_rows': 0,
            'error_count': 1
        }


@transaction.atomic
def save_questions_from_xlsm_data(data: List[Dict[str, Any]], subject_code: str) -> Dict[str, Any]:
    """XLSMデータから問題をデータベースに保存"""
    subject = Subject.objects.get(code=subject_code)
    saved_count = 0
    updated_count = 0
    errors = []
    
    for item in data:
        try:
            # 単元の取得または作成
            unit, created = Unit.objects.get_or_create(
                subject=subject,
                grade_year=item['grade'],
                category=item['category']
            )
            
            # 問題の取得または作成
            question, created = Question.objects.get_or_create(
                unit=unit,
                source_id=item['source_id'],
                defaults={
                    'question_type': item['question_type'],
                    'text': item['question_text'],
                    'correct_answer': item['correct_answer'],
                    'accepted_alternatives': item['alternatives'],
                    'choices': item['choices'],
                    'parts_count': item['parts_count'],
                    'requires_unit_label': item['requires_unit_label'],
                    'unit_label_text': item['unit_label_text'],
                }
            )
            
            if not created:
                # 既存の問題を更新
                question.question_type = item['question_type']
                question.text = item['question_text']
                question.correct_answer = item['correct_answer']
                question.accepted_alternatives = item['alternatives']
                question.choices = item['choices']
                question.parts_count = item['parts_count']
                question.requires_unit_label = item['requires_unit_label']
                question.unit_label_text = item['unit_label_text']
                question.save()
                updated_count += 1
            else:
                saved_count += 1
                
        except Exception as e:
            errors.append(f"問題保存エラー (ID: {item['source_id']}): {str(e)}")
    
    return {
        'saved_count': saved_count,
        'updated_count': updated_count,
        'errors': errors
    }
