from django import forms
from .models import XLSMUpload
from quiz_app.models import Question, Homework


class XLSMUploadForm(forms.ModelForm):
    """XLSMアップロードフォーム"""
    
    class Meta:
        model = XLSMUpload
        fields = ['subject', 'file']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class QuestionForm(forms.ModelForm):
    """問題編集フォーム"""
    
    class Meta:
        model = Question
        fields = ['text', 'correct_answer', 'accepted_alternatives', 'requires_unit_label', 'unit_label_text', 'parts_count']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'correct_answer': forms.TextInput(attrs={'class': 'form-control'}),
            'accepted_alternatives': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'requires_unit_label': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'unit_label_text': forms.TextInput(attrs={'class': 'form-control'}),
            'parts_count': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class HomeworkForm(forms.ModelForm):
    """宿題フォーム"""
    
    class Meta:
        model = Homework
        fields = ['unit', 'question_count', 'publish_scope', 'is_published']
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'question_count': forms.Select(attrs={'class': 'form-control'}),
            'publish_scope': forms.Select(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
