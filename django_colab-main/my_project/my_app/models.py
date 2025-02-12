# my_app/models.py

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

class Document(models.Model):
    docfile = models.FileField(
        upload_to='documents/%Y/%m/%d',
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'doc', 'docx', 'dot', 'dotx'])
        ]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document: {self.docfile.name}"

class MyModel(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    content = models.TextField()

    # The “upload” field for text extraction (PDF, doc, etc.)
    upload = models.FileField(
        upload_to='uploads/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'doc', 'docx', 'dot', 'dotx'])
        ]
    )

    # Optional image field
    cover_image = models.ImageField(upload_to='blog_covers/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('user_profile_detail', args=[str(self.pk)])

    def __str__(self):
        return self.user.username
