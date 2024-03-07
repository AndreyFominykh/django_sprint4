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
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Count

from blog.models import Category, Post, Comment
from .forms import CommentForm, PostForm, ProfileForm


POSTS_QNT = 10


class QuerySet:
    def get_queryset(self):
        return Post.objects.select_related(
            'author', 'location', 'category'
        ).filter(is_published=True, category__is_published=True,
                 pub_date__lte=timezone.now()).order_by('-pub_date').all()


class PostFormMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if post.author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class ProfileListView(LoginRequiredMixin, QuerySet, ListView):
    """Страница профиля залогиненного пользователя"""

    model = User
    template_name = 'blog/profile.html'
    form = ProfileForm
    paginate_by = POSTS_QNT

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        queryset = Post.objects
        self.profile = get_object_or_404(User,
                                         username=self.kwargs['username'])
        queryset = queryset.filter(
            author=self.profile).annotate(comment_count=Count(
                'comments')).order_by('-pub_date')
        if self.request.user != self.profile:
            queryset = super().get_queryset().annotate(
                comment_count=Count('comments'))
        return queryset

    def get_context_data(self, **kwargs):
        return dict(**super().get_context_data(**kwargs),
                    profile=self.get_object())


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля залогиненного пользователя"""

    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        user = get_object_or_404(User, username=self.request.user)
        return user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


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

    form_class = PostForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs) -> HttpResponse:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user != post.author:
            return post
        return get_object_or_404(Post, is_published=True,
                                 category__is_published=True,
                                 pub_date__lte=timezone.now(),
                                 pk=self.kwargs['post_id'])


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создаём пост"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Проверяем валидность формы"""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляем пользователя на его страницу"""
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Редактируем пост"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_id = kwargs['post_id']
        instance = get_object_or_404(Post, pk=self.post_id)
        if instance.author != request.user:
            return redirect('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})
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


class PostCategoryView(QuerySet, ListView):
    paginate_by = POSTS_QNT
    context = 'post_list'
    template_name = 'blog/category.html'

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        self.category = get_object_or_404(Category,
                                          slug=self.kwargs['category_slug'],
                                          is_published=True)
        return super().get_queryset().filter(category__slug=category_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categpry'] = self.category
        return context


@login_required
def add_comment(request, post_id) -> HttpResponse:
    """Комменты только для залогиненных пользователей"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', id=post_id)


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
