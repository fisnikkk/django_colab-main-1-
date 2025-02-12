# my_app/views.py
import PyPDF2
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponseNotAllowed
from django.core.exceptions import PermissionDenied

import os
import docx

from django.shortcuts import render, redirect
from .forms import BlogPostForm, UserProfileForm, DocumentForm, CreateUserForm
from .models import BlogPost, UserProfile, User, Document

# ====== AUTH / PASSWORD / USER PROFILE ======
@csrf_exempt
def extract_pdf_text(request):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf_file')
        if not pdf_file:
            return JsonResponse({'success': False, 'error': 'No file'}, status=400)
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            content = ""
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    content += text + "\n"
            return JsonResponse({'success': True, 'text': content})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)  # Create a UserProfile for the new user
            login(request, user)
            return redirect('blog_post_list')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def manage_users(request):
    # Only staff can see this page
    if not request.user.is_staff:
        raise PermissionDenied("You must be staff to access this page.")

    all_users = User.objects.all()
    return render(request, 'manage_users.html', {'all_users': all_users})

@login_required
def create_user(request):
    # Only staff can create new users
    if not request.user.is_staff:
        raise PermissionDenied("You must be staff to create new users.")

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()  # Possibly sets is_staff if 'make_staff' is checked
            return redirect('manage_users')
    else:
        form = CreateUserForm()
    return render(request, 'create_user.html', {'form': form})

@login_required
def toggle_staff_status(request, user_id):
    # Only staff can do this
    if not request.user.is_staff:
        raise PermissionDenied("You must be staff to toggle staff status.")

    user_to_toggle = get_object_or_404(User, pk=user_id)
    user_to_toggle.is_staff = not user_to_toggle.is_staff
    user_to_toggle.save()
    return redirect('manage_users')

# ====== USER PROFILE ======

def user_profile_list(request):
    users = User.objects.all()
    return render(request, 'user_profile_list.html', {'users': users})

class UserProfileDetailView(LoginRequiredMixin, DetailView):
    model = UserProfile
    context_object_name = 'user_profile'
    template_name = 'user_profile_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(UserProfile, user=self.request.user)

class UserProfileCreateView(CreateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'user_profile_form.html'
    success_url = '/user_profiles/'

class UserProfileUpdateView(UpdateView):
    model = User  # note: this updates the User, not UserProfile
    form_class = UserProfileForm
    template_name = 'user_profile_form.html'
    success_url = '/user_profiles/'

class UserProfileDeleteView(DeleteView):
    model = User
    template_name = 'user_profile_confirm_delete.html'
    success_url = '/user_profiles/'

# ====== DOCUMENTS / IMAGES ======

def upload_file(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_success')
    else:
        form = DocumentForm()
    return render(request, 'upload.html', {'form': form})

def display_images(request):
    images = Document.objects.all()
    return render(request, 'display_images.html', {'images': images})

def delete_image(request, image_id):
    if request.method == 'POST':
        image = get_object_or_404(Document, pk=image_id)
        image.docfile.delete()  # remove file from storage
        image.delete()          # remove record
        return redirect('display_images')
    return HttpResponseNotAllowed(['POST'])

def delete_all_images(request):
    if request.method == 'POST':
        documents = Document.objects.all()
        for doc in documents:
            if doc.docfile:
                doc.docfile.delete(save=False)
            doc.delete()
        return redirect('display_images')
    return HttpResponseNotAllowed(['POST'])

def upload_success(request):
    return render(request, 'upload_success.html')

# ====== BLOG POST CRUD & SEARCH ======

@method_decorator(login_required, name='dispatch')
class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog_post_list.html'
    context_object_name = 'blog_posts'

class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog_post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # rename the context key if needed
        context['blog_post'] = context.pop('blogpost')
        return context


class BlogPostUpdateView(UpdateView):
    model = BlogPost
    fields = ['title', 'author', 'content']
    template_name = 'blog_post_update.html'
    success_url = reverse_lazy('blog_post_list')

class BlogPostDeleteView(DeleteView):
    model = BlogPost
    template_name = 'blog_post_delete.html'
    success_url = '/'

# ====== Searching for Blog Posts ======

def search(request):
    query = request.GET.get('q')
    if query:
        words = query.split()
        query_filter = Q()
        for word in words:
            query_filter |= Q(title__icontains=word) | Q(content__icontains=word)
        results = BlogPost.objects.filter(query_filter)
    else:
        results = []
    return render(request, 'search.html', {'results': results})

def search_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) > 2:
        suggestions = BlogPost.objects.filter(title__icontains=query)[:5].values('id', 'title')
    else:
        suggestions = []
    return JsonResponse({'suggestions': list(suggestions)})

# ====== UTILS FOR DOC EXTRACTION ======

def read_docx_file(file):
    import docx
    doc = docx.Document(file)
    content = "\n".join([p.text for p in doc.paragraphs])
    return content

# ====== CREATE BLOG POST WITH FILE EXTRACTION ======

def blog_post_create(request):
    """
    Allows user to create a BlogPost and if a file is uploaded,
    tries to extract its text into 'content'.
    """
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            uploaded_file = request.FILES.get('upload')
            if uploaded_file:
                # get extension in lowercase, including dot, e.g. ".pdf"
                file_extension = os.path.splitext(uploaded_file.name)[1].lower()

                if file_extension == '.txt':
                    try:
                        content = uploaded_file.read().decode()
                        post.content = content
                    except Exception as e:
                        messages.error(request, f"Error reading txt file: {e}")
                        return render(request, 'blog_post_create.html', {'form': form})

                elif file_extension in ['.doc', '.docx', '.dot', '.dotx']:
                    try:
                        content = read_docx_file(uploaded_file)
                        post.content = content
                    except Exception as e:
                        messages.error(request, f"Error extracting text from Word file: {e}")
                        return render(request, 'blog_post_create.html', {'form': form})

                elif file_extension == '.pdf':
                    try:
                        import PyPDF2
                        pdf_reader = PyPDF2.PdfReader(uploaded_file)  # in older versions it's PyPDF2.PdfFileReader
                        content = ""
                        for page in pdf_reader.pages:
                            text = page.extract_text()
                            if text:
                                content += text
                        post.content = content
                    except Exception as e:
                        messages.error(request, f"Error extracting text from PDF: {e}")
                        return render(request, 'blog_post_create.html', {'form': form})

                else:
                    # If we ever get an extension not in [txt, doc, docx, dot, dotx, pdf]
                    # Even though the model validator should forbid it, we also check here:
                    messages.error(request, 'Unsupported file format. Please upload a txt, doc, docx, dot, dotx, or pdf file.')
                    return render(request, 'blog_post_create.html', {'form': form})

            # If no file or no text extracted, just proceed with whatever is in 'content' field
            post.save()
            messages.success(request, "Blog post created successfully!")
            return redirect('blog_post_list')
        else:
            messages.error(request, 'There were errors in the form.')
    else:
        form = BlogPostForm()

    return render(request, 'blog_post_create.html', {'form': form})
