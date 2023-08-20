from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['title', 'description']
        labels = {
            'title': 'Title',
            'description': 'Description',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EditCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['title', 'description']