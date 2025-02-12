from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User



class Document(models.Model):
    # docfile = models.FileField(upload_to='documents/')
    docfile = models.ImageField(upload_to='documents/%Y/%m/%d')
    uploaded_at = models.DateTimeField(auto_now_add=True)


# my_app/models.py

class MyModel(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    content = models.TextField()
    upload = models.FileField(upload_to='uploads/', blank=True, null=True)  # Document for text extraction
    cover_image = models.ImageField(upload_to='blog_covers/', blank=True, null=True)  # Cover image field

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