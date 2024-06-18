from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Classroom, Assignment, Quiz, Announcement, ClassComment, PrivateMessage, Material

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('user_type', 'profile_picture')

class ClassroomCreationForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name']

class JoinClassroomForm(forms.Form):
    code = forms.CharField(max_length=10)

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'file', 'due_date']

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'question', 'option1', 'option2', 'option3', 'option4', 'correct_option']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content']

class ClassCommentForm(forms.ModelForm):
    class Meta:
        model = ClassComment
        fields = ['content']

class PrivateMessageForm(forms.ModelForm):
    class Meta:
        model = PrivateMessage
        fields = ['receiver', 'content']

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['title', 'file', 'description']
