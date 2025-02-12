# my_app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from .models import UserProfile, Document, BlogPost

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('docfile',)
        widgets = {
            # If you want to hint the browser to accept PDF, doc, etc.:
            'docfile': forms.ClearableFileInput(attrs={
                'accept': '.pdf,.txt,.doc,.docx,.dot,.dotx,image/*'
            }),
        }

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'author', 'content', 'upload', 'cover_image']
        # If you like, you can also add a `widget` for the 'upload' field:
        # widgets = {
        #     'upload': forms.ClearableFileInput(
        #         attrs={'accept': '.pdf,.txt,.doc,.docx,.dot,.dotx'}
        #     )
        # }

class SearchForm(forms.Form):
    query = forms.CharField()

class UserProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, help_text="Required.")
    email = forms.EmailField(max_length=254, required=True, help_text="Required.")
    password = forms.CharField(widget=forms.PasswordInput, required=True, help_text="Required.")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class CreateUserForm(forms.ModelForm):
    make_staff = forms.BooleanField(required=False, help_text="Check to make this user staff")

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "password": forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        raw_pw = self.cleaned_data["password"]
        user.set_password(raw_pw)

        if self.cleaned_data.get("make_staff"):
            user.is_staff = True

        if commit:
            user.save()
        return user
