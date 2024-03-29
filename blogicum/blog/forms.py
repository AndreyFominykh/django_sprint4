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
        exclude = ('author',)
        widgets = {'pub_date':
                   forms.DateTimeInput(format='%d/%m/%Y %H:%M',
                                       attrs={'type': 'datetime-local'})}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)
