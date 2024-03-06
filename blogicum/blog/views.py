from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http.response import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import (DetailView, CreateView, DeleteView, ListView,
                                  UpdateView)
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Count

from blog.models import Category, Post, Comment
from .forms import CommentForm, PostForm, ProfileForm


POSTS_QNT = 10


def published_posts():
    return Post.objects.select_related(
        'category', 'location', 'author').filter(
        is_published=True, category__is_published=True,
        pub_date__lte=timezone.now())


class UserDetailView(LoginRequiredMixin, DetailView):
    """Страница профиля залогиненного пользователя"""

    model = User
    template_name = 'blog/profile.html'
    paginate_by = POSTS_QNT

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля залогиненного пользователя"""

    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        user = get_object_or_404(User, username=self.request.username)
        return user

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile', kwargs={'username': self.username})


class IndexListView(ListView):
    """Показывает ленту записей"""

    model = Post
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = POSTS_QNT
    queryset = Post.objects.filter(is_published=True,
                                   category__is_published=True,
                                   pub_date__lte=timezone.now()).annotate(
                                       comment_count=Count('comments'))


class PostDetailView(DetailView):
    """Полный текст поста"""

    model = Post
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if not instance.is_published and instance.author != request.user:
            raise Http404('')
        return super().dispatch(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создаём пост"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Проверяем валидность формы"""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> HttpResponse:
        """Перенаправляем пользователя на его страницу"""
        if self.request.user.is_authenticated:
            return redirect('blog:profile', args=(
                self.request.user.get_username(),))
        else:
            return redirect('login')


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Редактируем пост"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_id = kwargs['pk']
        instance = get_object_or_404(Post, pk=self.post_id)
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=self.post_id)
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Удаляем пост"""

    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


def category_posts(request, category_slug) -> HttpResponse:
    """Посты одной категории"""
    category = get_object_or_404(Category.objects.filter(
        is_published=True), slug=category_slug)
    post_list = published_posts().filter(
        category__slug=category_slug)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


@login_required
def add_comment(request, pk) -> HttpResponse:
    """Комменты только для залогиненных пользователей"""
    comment = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = comment
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, comment_id, post_id) -> HttpResponse:
    """Редактируем комменты"""
    instance = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if instance.author != request.user:
        return redirect('login')
    form = CommentForm(request.POST or None, instance=instance)
    context = {'form': form, 'comment': instance}
    if form.is_valid():
        form.save
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, comment_id, post_id) -> HttpResponse:
    """Удаляем комменты"""
    instance = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if instance.author != request.user:
        return redirect('login')
    context = {'comment': instance}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)
