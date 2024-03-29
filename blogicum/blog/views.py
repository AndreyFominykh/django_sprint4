from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import (DetailView, CreateView, DeleteView, ListView,
                                  UpdateView)
from django.urls import reverse_lazy, reverse
from django.db.models import Count
from django.http import Http404

from blog.models import Category, Post, Comment
from .forms import CommentForm, PostForm, ProfileForm


POSTS_QNT = 10


def base_function(add_filter=False, add_count_comment=False):
    features = Post.objects.select_related('category', 'author',
                                           'location')
    if add_filter:
        features = features.filter(is_published=True,
                                   category__is_published=True,
                                   pub_date__lte=timezone.now())
    if add_count_comment:
        features = features.annotate(
            comment_count=Count('comments')).order_by('-pub_date')
    return features


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse('blog:profile', args=[self.request.user.username])


class ProfileListView(ListView):
    """Страница профиля залогиненного пользователя"""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_QNT

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        profile = self.get_object()
        is_author = self.request.user == profile
        return base_function(add_filter=not is_author,
                             add_count_comment=True).filter(author=profile)

    def get_context_data(self, **kwargs):
        return dict(**super().get_context_data(**kwargs),
                    profile=self.get_object())


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля залогиненного пользователя"""

    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class IndexListView(ListView):
    """Показывает ленту записей"""

    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = POSTS_QNT
    queryset = base_function(add_filter=True, add_count_comment=True)


class PostDetailView(DetailView):
    """Полный текст поста"""

    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs) -> HttpResponse:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context

    def get_object(self):
        post = get_object_or_404(Post.objects.all()
                                 .select_related(
                                     'location',
                                     'category',
                                     'author'), pk=self.kwargs.get('post_id'))
        if post.author != self.request.user:
            if (
                post.is_published is not True
                or post.pub_date > timezone.now()
                or post.category.is_published is not True
            ):
                raise Http404
        return post


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создаём пост"""

    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Проверяем валидность формы"""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляем пользователя на его страницу"""
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    """Редактируем пост"""

    pass


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):
    """Удаляем пост"""

    pass


class PostCategoryView(ListView):
    paginate_by = POSTS_QNT
    template_name = 'blog/category.html'

    def get_object(self):
        return get_object_or_404(Category,
                                 slug=self.kwargs['category_slug'],
                                 is_published=True)

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        return base_function(add_filter=True,
                             add_count_comment=True).filter(
                                 category__slug=category_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_object()
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
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, comment_id, post_id) -> HttpResponse:
    """Редактируем комменты"""
    instance = get_object_or_404(Comment, id=comment_id)
    if instance.author != request.user:
        return redirect('login')
    form = CommentForm(request.POST or None, instance=instance)
    context = {'form': form, 'comment': instance}
    if form.is_valid():
        comment = form.save(commit=False)
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)
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
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)
