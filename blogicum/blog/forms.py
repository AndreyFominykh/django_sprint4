from django import forms
from django.contrib.auth import get_user_model

from .models import Post, Comment


User = get_user_model()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {'pub_date': forms.DateInput(format='%d/%m/%Y %H:%M',
                                               attrs={'type': 'date'})}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)