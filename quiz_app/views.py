import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.contrib import messages
from .models import Subject, Unit, Question, QuizSession, QuizAttempt, Homework
from .utils import check_answer

# ロガーを設定
logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """ホームページ"""
    template_name = 'quiz_app/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subjects'] = Subject.objects.all()
        return context


class SubjectView(DetailView):
    """教科詳細ページ"""
    model = Subject
    template_name = 'quiz_app/subject.html'
    context_object_name = 'subject'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['units'] = self.object.units.all().order_by('grade_year', 'category')
        return context


class UnitView(DetailView):
    """単元詳細ページ"""
    model = Unit
    template_name = 'quiz_app/unit.html'
    context_object_name = 'unit'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question_count'] = self.object.questions.count()
        return context


class QuizStartView(LoginRequiredMixin, TemplateView):
    """クイズ開始ページ"""
    template_name = 'quiz_app/quiz_start.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unit_id = self.kwargs['unit_id']
        question_count = self.kwargs['question_count']
        
        unit = get_object_or_404(Unit, id=unit_id)
        context['unit'] = unit
        context['question_count'] = question_count
        
        # クイズセッションを作成
        session = QuizSession.objects.create(
            user=self.request.user,
            unit=unit,
            question_count=question_count
        )
        context['session'] = session
        
        return context


class QuizQuestionView(LoginRequiredMixin, TemplateView):
    """クイズ問題ページ"""
    template_name = 'quiz_app/quiz_question.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = self.kwargs['session_id']
        question_number = self.kwargs['question_number']
        
        session = get_object_or_404(QuizSession, id=session_id, user=self.request.user)
        context['session'] = session
        
        # 問題を取得（保存された問題IDがある場合はそれを使用、なければランダム）
        if session.question_ids and str(question_number) in session.question_ids:
            # 保存された問題IDを使用（間違い再挑戦など）
            question_id = session.question_ids[str(question_number)]
            question = get_object_or_404(Question, id=question_id)
            logger.info(f"保存された問題IDを使用: 問題番号={question_number}, 問題ID={question_id}, 問題文={question.text[:50]}...")
        else:
            # ランダムに問題を選択（通常のクイズ）
            questions = list(session.unit.questions.all())
            if question_number <= len(questions):
                # 既に使用された問題IDを除外
                used_question_ids = set()
                if session.question_ids:
                    used_question_ids = set(session.question_ids.values())
                
                # 未使用の問題のみから選択
                available_questions = [q for q in questions if q.id not in used_question_ids]
                if available_questions:
                    import random
                    question = random.choice(available_questions)
                else:
                    # すべての問題を使用済みの場合は最初の問題を使用
                    question = questions[0]
                
                # セッションに問題IDを保存（問題番号ごと）
                if not session.question_ids:
                    session.question_ids = {}
                session.question_ids[str(question_number)] = question.id
                session.save()
                logger.info(f"新しい問題を選択: 問題番号={question_number}, 問題ID={question.id}, 問題文={question.text[:50]}...")
        
        # 選択問題の場合、選択肢をランダムに並べ替え
        if question.question_type == 'choice' and question.choices:
            import random
            # 選択肢のコピーを作成してランダムに並べ替え
            shuffled_choices = question.choices.copy()
            random.shuffle(shuffled_choices)
            question.shuffled_choices = shuffled_choices
            
            # 選択肢の並べ替え情報をセッションに保存
            if not session.choice_mappings:
                session.choice_mappings = {}
            
            # 問題IDごとに選択肢の並べ替え情報を保存
            session.choice_mappings[str(question.id)] = shuffled_choices
            session.save()
        
        context['question'] = question
        context['question_number'] = question_number
        context['total_questions'] = session.question_count
        
        return context


class QuizResultView(LoginRequiredMixin, DetailView):
    """クイズ結果ページ"""
    model = QuizSession
    template_name = 'quiz_app/quiz_result.html'
    context_object_name = 'session'
    
    def get_queryset(self):
        return QuizSession.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        
        # 解答記録を取得
        attempts = session.attempts.all().select_related('question')
        context['attempts'] = attempts
        
        # 統計情報
        correct_count = attempts.filter(is_correct=True).count()
        total_time = attempts.aggregate(total=Avg('time_spent_sec'))['total'] or 0
        
        # 時間を分と秒に変換
        if total_time >= 60:
            minutes = int(total_time // 60)
            seconds = int(total_time % 60)
            time_display = f"{minutes}分{seconds}秒"
        else:
            time_display = f"{int(total_time)}秒"
        
        context['correct_count'] = correct_count
        context['total_questions'] = session.question_count
        context['score'] = (correct_count / session.question_count) * 100
        context['average_time'] = total_time
        context['time_display'] = time_display
        
        # 単元全体の正答率を計算
        unit_attempts = QuizAttempt.objects.filter(question__unit=session.unit)
        if unit_attempts.count() > 0:
            unit_correct_rate = (unit_attempts.filter(is_correct=True).count() / unit_attempts.count()) * 100
            context['unit_correct_rate'] = round(unit_correct_rate, 1)
        else:
            context['unit_correct_rate'] = 0
        
        # 各問題の正答率を計算と選択肢の内容を追加
        for attempt in attempts:
            # その問題の全解答記録から正答率を計算
            question_attempts = QuizAttempt.objects.filter(question=attempt.question)
            if question_attempts.count() > 0:
                question_correct_rate = (question_attempts.filter(is_correct=True).count() / question_attempts.count()) * 100
                attempt.question_correct_rate = round(question_correct_rate, 1)
            else:
                attempt.question_correct_rate = 0
            
            # 選択問題の場合、選択肢の内容を追加
            if attempt.question.question_type == 'choice':
                try:
                    # ユーザーの答えが数字の場合、選択肢の内容を取得
                    choice_index = int(attempt.answer_text) - 1
                    
                    # セッションに保存された選択肢の並べ替え情報を使用
                    if session.choice_mappings and str(attempt.question.id) in session.choice_mappings:
                        shuffled_choices = session.choice_mappings[str(attempt.question.id)]
                        if 0 <= choice_index < len(shuffled_choices):
                            attempt.selected_choice_text = shuffled_choices[choice_index]
                        else:
                            attempt.selected_choice_text = attempt.answer_text
                    else:
                        # 選択肢の並べ替え情報がない場合は元の選択肢配列を使用
                        if 0 <= choice_index < len(attempt.question.choices):
                            attempt.selected_choice_text = attempt.question.choices[choice_index]
                        else:
                            attempt.selected_choice_text = attempt.answer_text
                except ValueError:
                    # 数字でない場合はそのまま表示
                    attempt.selected_choice_text = attempt.answer_text
            else:
                attempt.selected_choice_text = attempt.answer_text
        
        return context


class QuizRetryView(LoginRequiredMixin, DetailView):
    """間違い再挑戦ページ"""
    model = QuizSession
    template_name = 'quiz_app/quiz_retry.html'
    context_object_name = 'session'
    
    def get_queryset(self):
        return QuizSession.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        
        # 間違えた問題を取得
        incorrect_attempts = session.attempts.filter(is_correct=False)
        incorrect_questions = [attempt.question for attempt in incorrect_attempts]
        
        context['incorrect_questions'] = incorrect_questions
        context['incorrect_count'] = len(incorrect_questions)
        return context


class QuizRetryStartView(LoginRequiredMixin, DetailView):
    """間違い再挑戦開始ページ"""
    model = QuizSession
    template_name = 'quiz_app/quiz_retry_start.html'
    context_object_name = 'session'
    
    def get_queryset(self):
        return QuizSession.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        
        # 間違えた問題を取得
        incorrect_attempts = session.attempts.filter(is_correct=False)
        incorrect_questions = [attempt.question for attempt in incorrect_attempts]
        
        # 新しいセッションを作成（間違いのみ）
        retry_session = QuizSession.objects.create(
            user=self.request.user,
            unit=session.unit,
            question_count=len(incorrect_questions),
            question_ids={}  # 間違い問題のIDを保存
        )
        
        # 間違い問題のIDをセッションに保存
        for i, question in enumerate(incorrect_questions, 1):
            retry_session.question_ids[str(i)] = question.id
        retry_session.save()
        
        context['retry_session'] = retry_session
        context['incorrect_questions'] = incorrect_questions
        context['incorrect_count'] = len(incorrect_questions)
        return context


class MyPageView(LoginRequiredMixin, TemplateView):
    """生徒マイページ"""
    template_name = 'quiz_app/mypage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.role == 'student':
            # 生徒の統計情報
            sessions = QuizSession.objects.filter(user=user)
            attempts = QuizAttempt.objects.filter(session__user=user)
            
            context['total_sessions'] = sessions.count()
            context['total_attempts'] = attempts.count()
            context['total_time'] = attempts.aggregate(total=Avg('time_spent_sec'))['total'] or 0
            context['average_time_per_question'] = attempts.aggregate(avg=Avg('time_spent_sec'))['avg'] or 0
            context['correct_rate'] = (attempts.filter(is_correct=True).count() / attempts.count() * 100) if attempts.count() > 0 else 0
            
            # 最近のセッション
            context['recent_sessions'] = sessions.order_by('-started_at')[:5]
        
        return context


class ProfileEditView(LoginRequiredMixin, TemplateView):
    """プロファイル編集ページ"""
    template_name = 'quiz_app/profile_edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.role == 'student':
            try:
                profile = user.student_profile
            except:
                profile = None
        else:
            try:
                profile = user.admin_profile
            except:
                profile = None
        
        context['profile'] = profile
        return context
    
    def post(self, request, *args, **kwargs):
        user = request.user
        
        if user.role == 'student':
            try:
                profile = user.student_profile
            except:
                profile = None
            
            if profile:
                # 生徒プロファイルの更新
                profile.prefecture = request.POST.get('prefecture', '')
                profile.school = request.POST.get('school', '')
                profile.class_name = request.POST.get('class_name', '')
                profile.nickname = request.POST.get('nickname', '')
                profile.grade = request.POST.get('grade', '')
                profile.save()
                
                messages.success(request, 'プロファイルを更新しました。')
                return redirect('quiz_app:mypage')
        else:
            try:
                profile = user.admin_profile
            except:
                profile = None
            
            if profile:
                # 管理者プロファイルの更新
                profile.name = request.POST.get('name', '')
                profile.email = request.POST.get('email', '')
                profile.save()
                
                messages.success(request, 'プロファイルを更新しました。')
                return redirect('quiz_app:mypage')
        
        messages.error(request, 'プロファイルの更新に失敗しました。')
        return redirect('quiz_app:profile_edit')


class RankingView(TemplateView):
    """匿名ランキングページ"""
    template_name = 'quiz_app/ranking.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 総プレイ数ランキング
        play_count_ranking = QuizSession.objects.values('user__student_profile__nickname').annotate(
            total_sessions=Count('id')
        ).order_by('-total_sessions')[:10]
        
        # 1問あたり平均時間ランキング
        avg_time_ranking = QuizAttempt.objects.values('session__user__student_profile__nickname').annotate(
            avg_time=Avg('time_spent_sec')
        ).order_by('avg_time')[:10]
        
        context['play_count_ranking'] = play_count_ranking
        context['avg_time_ranking'] = avg_time_ranking
        
        return context


class HomeworkView(TemplateView):
    """宿題ページ"""
    template_name = 'quiz_app/homework.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']
        homework = get_object_or_404(Homework, public_slug=slug, is_published=True)
        context['homework'] = homework
        return context


# API Views
@method_decorator(csrf_exempt, name='dispatch')
class SubmitAnswerView(LoginRequiredMixin, TemplateView):
    """解答提出API"""
    template_name = 'quiz_app/partials/answer_result.html'
    
    def post(self, request, *args, **kwargs):
        session_id = request.POST.get('session_id')
        question_id = request.POST.get('question_id')
        answer_text = request.POST.get('answer_text')
        time_spent = request.POST.get('time_spent', 0)
        
        session = get_object_or_404(QuizSession, id=session_id, user=request.user)
        question = get_object_or_404(Question, id=question_id)
        
        # 採点ロジック（簡易版）
        is_correct = self.check_answer(answer_text, question)
        
        # 解答記録を保存
        QuizAttempt.objects.create(
            session=session,
            question=question,
            answer_text=answer_text,
            is_correct=is_correct,
            time_spent_sec=int(time_spent)
        )
        
        context = {
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'question': question
        }
        
        return render(request, self.template_name, context)
    
    def check_answer(self, user_answer, question):
        """採点ロジック"""
        return check_answer(user_answer, question)


@login_required
def submit_answer(request, session_id, question_number):
    """解答提出処理"""
    if request.method == 'POST':
        session = get_object_or_404(QuizSession, id=session_id, user=request.user)
        
        # 問題を取得（保存された問題IDを使用）
        if session.question_ids and str(question_number) in session.question_ids:
            question_id = session.question_ids[str(question_number)]
            question = get_object_or_404(Question, id=question_id)
            logger.info(f"submit_answer: 保存された問題IDを使用: 問題番号={question_number}, 問題ID={question_id}, 問題文={question.text[:50]}...")
        else:
            # 問題IDが保存されていない場合はエラー
            logger.error(f"submit_answer: 問題IDが見つかりません: 問題番号={question_number}, セッションID={session_id}")
            return redirect('quiz_app:home')
        
        # 解答を取得（複数解答欄対応）
        if question.parts_count == 1:
            answer_text = request.POST.get('answer_1', '')
            
            # 選択問題の場合、選択肢の内容を取得
            if question.question_type == 'choice':
                try:
                    choice_index = int(answer_text) - 1
                    
                    # セッションに保存された選択肢の並べ替え情報を使用
                    if session.choice_mappings and str(question.id) in session.choice_mappings:
                        shuffled_choices = session.choice_mappings[str(question.id)]
                        if 0 <= choice_index < len(shuffled_choices):
                            answer_text = shuffled_choices[choice_index]
                    elif hasattr(question, 'shuffled_choices'):
                        # フォールバック: 問題オブジェクトの並べ替え情報を使用
                        if 0 <= choice_index < len(question.shuffled_choices):
                            answer_text = question.shuffled_choices[choice_index]
                except ValueError:
                    pass  # 数字でない場合はそのまま使用
        else:
            answers = []
            for i in range(1, question.parts_count + 1):
                answer = request.POST.get(f'answer_{i}', '')
                answers.append(answer)
            
            answer_text = '・'.join(answers)
        
        # 採点
        is_correct = check_answer(answer_text, question)
        
        # 実際の解答時間を取得
        time_spent = request.POST.get('time_spent', 20)
        try:
            time_spent = int(time_spent)
        except ValueError:
            time_spent = 20
        
        # 解答記録を保存
        QuizAttempt.objects.create(
            session=session,
            question=question,
            answer_text=answer_text,
            is_correct=is_correct,
            time_spent_sec=time_spent
        )
        
        # 次の問題または結果ページへ
        if question_number < session.question_count:
            return redirect('quiz_app:quiz_question', session_id=session_id, question_number=question_number + 1)
        else:
            # クイズ終了処理
            session.finished_at = timezone.now()
            session.total_score = (session.attempts.filter(is_correct=True).count() / session.question_count) * 100
            session.save()
            return redirect('quiz_app:quiz_result', pk=session_id)
    
    return redirect('quiz_app:home')


class QuizStatusView(LoginRequiredMixin, TemplateView):
    """クイズ状態確認API"""
    template_name = 'quiz_app/partials/quiz_status.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = self.kwargs['pk']
        session = get_object_or_404(QuizSession, id=session_id, user=self.request.user)
        
        context['session'] = session
        context['attempts'] = session.attempts.all()
        
        return context
