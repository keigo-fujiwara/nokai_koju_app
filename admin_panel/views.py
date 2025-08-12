from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from .models import XLSMUpload, AnalyticsData, PDFTemplate, SystemLog
from .forms import XLSMUploadForm, QuestionForm, HomeworkForm
from quiz_app.models import Question, Unit, Homework


def admin_required(user):
    """管理者権限チェック"""
    return user.is_authenticated and user.role == 'admin'


class AdminRequiredMixin(UserPassesTestMixin):
    """管理者権限が必要なMixin"""
    
    def test_func(self):
        return admin_required(self.request.user)


class AdminHomeView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """管理画面ホーム"""
    template_name = 'admin_panel/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 統計情報
        context['total_questions'] = Question.objects.count()
        context['total_units'] = Unit.objects.count()
        context['recent_uploads'] = XLSMUpload.objects.order_by('-uploaded_at')[:5]
        context['recent_logs'] = SystemLog.objects.order_by('-created_at')[:5]
        
        return context


class XLSMUploadView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """XLSMアップロード"""
    model = XLSMUpload
    template_name = 'admin_panel/upload.html'
    form_class = XLSMUploadForm
    success_url = reverse_lazy('admin_panel:home')
    
    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        form.instance.status = 'processing'
        response = super().form_valid(form)
        
        # バックグラウンドで処理を実行
        import threading
        
        def process_file():
            try:
                from quiz_app.utils import process_xlsm_file, save_questions_from_xlsm_data
                from django.utils import timezone
                
                # ファイルパスを取得
                file_path = form.instance.file.path
                print(f"DEBUG: ファイルパス: {file_path}")
                
                # ファイルを処理
                result = process_xlsm_file(file_path, form.instance.subject)
                print(f"DEBUG: 処理結果 - データ数: {result['total_rows']}, エラー数: {result['error_count']}")
                
                if result['error_count'] > 0:
                    # エラーがある場合
                    form.instance.status = 'failed'
                    form.instance.error_message = '\n'.join(result['errors'][:10])
                    form.instance.processed_at = timezone.now()
                    form.instance.save()
                else:
                    # データベースに保存
                    save_result = save_questions_from_xlsm_data(result['data'], form.instance.subject)
                    print(f"DEBUG: 保存結果 - 新規: {save_result['saved_count']}, 更新: {save_result['updated_count']}")
                    
                    if save_result['errors']:
                        form.instance.status = 'failed'
                        form.instance.error_message = '\n'.join(save_result['errors'][:10])
                    else:
                        form.instance.status = 'completed'
                        form.instance.error_message = f'新規: {save_result["saved_count"]}件, 更新: {save_result["updated_count"]}件'
                    
                    form.instance.processed_at = timezone.now()
                    form.instance.save()
                
            except Exception as e:
                print(f"DEBUG: 例外発生: {str(e)}")
                import traceback
                traceback.print_exc()
                form.instance.status = 'failed'
                form.instance.error_message = str(e)
                form.instance.processed_at = timezone.now()
                form.instance.save()
        
        # バックグラウンドスレッドで処理を開始
        thread = threading.Thread(target=process_file)
        thread.daemon = True
        thread.start()
        
        messages.success(self.request, 'ファイルがアップロードされました。処理中です。')
        return response


class XLSMPreviewView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """XLSMプレビュー"""
    model = XLSMUpload
    template_name = 'admin_panel/upload_preview.html'
    context_object_name = 'upload'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ここでXLSMファイルの内容を解析してプレビューを表示
        # 実際の実装ではopenpyxlを使用してファイルを読み込む
        return context


class XLSMConfirmView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """XLSM確定"""
    model = XLSMUpload
    template_name = 'admin_panel/upload_confirm.html'
    context_object_name = 'upload'
    
    def post(self, request, *args, **kwargs):
        upload = self.get_object()
        # ここでXLSMファイルの内容をデータベースに保存
        # 実際の実装ではopenpyxlを使用してファイルを読み込み、Questionモデルに保存
        upload.status = 'completed'
        upload.save()
        messages.success(request, 'データが正常に保存されました。')
        return redirect('admin_panel:home')


class UploadStatusView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """アップロード状況"""
    template_name = 'admin_panel/upload_status.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uploads'] = XLSMUpload.objects.order_by('-uploaded_at')[:10]
        return context


class QuestionListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """問題一覧"""
    model = Question
    template_name = 'admin_panel/questions.html'
    context_object_name = 'questions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Question.objects.select_related('unit').all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(text__icontains=search) |
                Q(unit__category__icontains=search) |
                Q(unit__grade_year__icontains=search)
            )
        return queryset.order_by('-created_at')


class QuestionEditView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """問題編集"""
    model = Question
    template_name = 'admin_panel/question_edit.html'
    form_class = QuestionForm
    success_url = reverse_lazy('admin_panel:questions')
    
    def form_valid(self, form):
        messages.success(self.request, '問題が更新されました。')
        return super().form_valid(form)


class QuestionDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """問題削除"""
    model = Question
    template_name = 'admin_panel/question_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:questions')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '問題が削除されました。')
        return super().delete(request, *args, **kwargs)


class AnalyticsView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """分析画面"""
    template_name = 'admin_panel/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 基本的な統計情報
        from accounts.models import StudentProfile
        from quiz_app.models import QuizSession, QuizAttempt
        
        context['total_students'] = StudentProfile.objects.count()
        context['total_attempts'] = QuizAttempt.objects.count()
        context['total_sessions'] = QuizSession.objects.count()
        
        # 平均正答率の計算
        total_attempts = QuizAttempt.objects.count()
        if total_attempts > 0:
            correct_attempts = QuizAttempt.objects.filter(is_correct=True).count()
            context['average_score'] = (correct_attempts / total_attempts) * 100
        else:
            context['average_score'] = 0
        
        return context


class ClassAnalyticsView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """クラス分析"""
    template_name = 'admin_panel/class_analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs['class_id']
        # クラス別の分析データを取得
        return context


class PDFGenerateView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """PDF生成"""
    template_name = 'admin_panel/pdf_generate.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unit_id = self.kwargs['unit_id']
        unit = get_object_or_404(Unit, id=unit_id)
        context['unit'] = unit
        return context
    
    def post(self, request, *args, **kwargs):
        unit_id = self.kwargs['unit_id']
        unit = get_object_or_404(Unit, id=unit_id)
        
        # PDF生成処理（実際の実装ではWeasyPrintを使用）
        # ここでは簡易的に成功メッセージを表示
        messages.success(request, f'{unit}のPDFが生成されました。')
        return redirect('admin_panel:home')


class HomeworkListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """宿題一覧"""
    model = Homework
    template_name = 'admin_panel/homework_list.html'
    context_object_name = 'homeworks'
    
    def get_queryset(self):
        return Homework.objects.filter(created_by=self.request.user).order_by('-created_at')


class HomeworkCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """宿題作成"""
    model = Homework
    template_name = 'admin_panel/homework_create.html'
    form_class = HomeworkForm
    success_url = reverse_lazy('admin_panel:homework_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        # 公開スラッグの生成
        import uuid
        form.instance.public_slug = str(uuid.uuid4())[:8]
        messages.success(self.request, '宿題が作成されました。')
        return super().form_valid(form)


class HomeworkEditView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """宿題編集"""
    model = Homework
    template_name = 'admin_panel/homework_edit.html'
    form_class = HomeworkForm
    success_url = reverse_lazy('admin_panel:homework_list')
    
    def get_queryset(self):
        return Homework.objects.filter(created_by=self.request.user)


class HomeworkDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """宿題削除"""
    model = Homework
    template_name = 'admin_panel/homework_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:homework_list')
    
    def get_queryset(self):
        return Homework.objects.filter(created_by=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '宿題が削除されました。')
        return super().delete(request, *args, **kwargs)
