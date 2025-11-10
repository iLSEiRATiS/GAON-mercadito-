from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'contenido', 'producto']
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Título', 'style': 'width:100%'}),
            'contenido': forms.Textarea(attrs={'rows': 6, 'style': 'width:100%'}),
        }
