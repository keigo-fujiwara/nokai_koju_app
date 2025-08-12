from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import User, StudentProfile, AdminProfile


class StudentRegistrationForm(UserCreationForm):
    """生徒登録フォーム"""
    
    member_id = forms.CharField(
        max_length=8,
        validators=[
            RegexValidator(
                regex=r'^\d{8}$',
                message='会員番号は8桁の数字で入力してください。'
            )
        ],
        help_text='8桁の数字で入力してください',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    prefecture = forms.CharField(max_length=10, label='都道府県', widget=forms.TextInput(attrs={'class': 'form-control'}))
    school = forms.CharField(max_length=100, label='所属校', widget=forms.TextInput(attrs={'class': 'form-control'}))
    class_name = forms.CharField(max_length=50, label='クラス', widget=forms.TextInput(attrs={'class': 'form-control'}))
    nickname = forms.CharField(max_length=50, label='ニックネーム', widget=forms.TextInput(attrs={'class': 'form-control'}))
    grade = forms.ChoiceField(
        choices=[
            ('中1', '中1'),
            ('中2', '中2'),
            ('中3', '中3'),
        ],
        label='学年',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'member_id', 'prefecture', 'school', 'class_name', 'nickname', 'grade', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
    
    def clean_member_id(self):
        member_id = self.cleaned_data['member_id']
        if StudentProfile.objects.filter(member_id=member_id).exists():
            raise forms.ValidationError('この会員番号は既に使用されています。')
        return member_id


class AdminRegistrationForm(UserCreationForm):
    """管理者登録フォーム"""
    
    name = forms.CharField(max_length=100, label='名前', widget=forms.TextInput(attrs={'class': 'form-control'}))
    employee_number = forms.CharField(max_length=20, label='社員番号', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='メールアドレス', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'name', 'employee_number', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
    
    def clean_employee_number(self):
        employee_number = self.cleaned_data['employee_number']
        if AdminProfile.objects.filter(employee_number=employee_number).exists():
            raise forms.ValidationError('この社員番号は既に使用されています。')
        return employee_number


class ProfileEditForm(forms.ModelForm):
    """プロファイル編集フォーム"""
    
    class Meta:
        model = User
        fields = ('email',)
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'student_profile'):
            # 生徒プロファイルのフィールドを追加
            self.fields['nickname'] = forms.CharField(
                max_length=50,
                initial=self.instance.student_profile.nickname,
                label='ニックネーム',
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
            self.fields['school'] = forms.CharField(
                max_length=100,
                initial=self.instance.student_profile.school,
                label='所属校',
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
            self.fields['class_name'] = forms.CharField(
                max_length=50,
                initial=self.instance.student_profile.class_name,
                label='クラス',
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
        elif hasattr(self.instance, 'admin_profile'):
            # 管理者プロファイルのフィールドを追加
            self.fields['name'] = forms.CharField(
                max_length=100,
                initial=self.instance.admin_profile.name,
                label='名前',
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            
            # プロファイルも更新
            if hasattr(user, 'student_profile'):
                profile = user.student_profile
                profile.nickname = self.cleaned_data.get('nickname', profile.nickname)
                profile.school = self.cleaned_data.get('school', profile.school)
                profile.class_name = self.cleaned_data.get('class_name', profile.class_name)
                profile.save()
            elif hasattr(user, 'admin_profile'):
                profile = user.admin_profile
                profile.name = self.cleaned_data.get('name', profile.name)
                profile.save()
        
        return user
