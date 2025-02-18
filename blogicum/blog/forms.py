from .models import Post, Comment
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)

class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
