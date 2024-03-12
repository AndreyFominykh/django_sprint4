from django.contrib.auth import get_user_model
from django.db import models

MAX_LEN = 256
User = get_user_model()


class PublishedModel(models.Model):
    """Абстрактная модель. Добавляем флаги is_published и created_at"""

    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано', help_text='Снимите галочку,'
        ' чтобы скрыть публикацию.')
    created_at = models.DateTimeField(
        verbose_name='Добавлено', auto_now_add=True)

    class Meta:
        abstract = True


class Category(PublishedModel):
    """Тематическая категория"""

    title = models.CharField(max_length=MAX_LEN, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True, verbose_name='Идентификатор', help_text=(
            'Идентификатор страницы для URL;'
            ' разрешены символы латиницы,'
            ' цифры, дефис и подчёркивание.'))

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    """Географическая метка"""

    name = models.CharField(max_length=MAX_LEN, verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    """Публикация"""

    title = models.CharField(
        max_length=MAX_LEN, verbose_name='Заголовок поста')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации', help_text='Если установить'
        ' дату и время в будущем — можно делать отложенные публикации.')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор публикации',
        related_name='blogs')
    location = models.ForeignKey(
        'Location', related_name='blogs', on_delete=models.SET_NULL, null=True,
        verbose_name='Местоположение', blank=True)
    category = models.ForeignKey(
        'Category', related_name='blogs', on_delete=models.SET_NULL, null=True,
        verbose_name='Категория')
    image = models.ImageField('Фото', upload_to='post_images', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date', ]

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Комменты к постам"""

    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post, verbose_name='Заголовок поста',
        on_delete=models.CASCADE, related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
