from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch


class PostQuerySet(models.QuerySet):
    def popular(self):
        """
        Аннотирует посты количеством лайков и возвращает ID самых популярных постов.
        """
        return self.annotate(likes_count=Count('likes')).order_by('-likes_count')

    def fetch_with_comments_count(self):
        """
        Для уже отфильтрованного QuerySet (например, самых популярных постов)
        аннотирует каждый пост количеством комментариев.
        """
        if not self.exists():
            return []

        post_ids = [post.id for post in self]

        comments_counts = Post.objects.filter(id__in=post_ids).annotate(
            comments_count=Count('comments')).values_list('id', 'comments_count')
        comments_count_dict = dict(comments_counts)

        updated_posts = []
        for post in self:
            post.comments_count = comments_count_dict.get(post.id, 0)
            updated_posts.append(post)

        return updated_posts

    def prefetch_tags(self, tags):
        prefetch = Prefetch('tags', queryset=tags)
        return self.prefetch_related("author", prefetch)


class TagQuerySet(models.QuerySet):

    def popular(self):
        popular_tags = self.annotate(
            posts_count=Count('posts')).order_by('-posts_count')
        return popular_tags


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})


class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True)

    objects = TagQuerySet.as_manager()

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    def clean(self):
        self.title = self.title.lower()


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Пост, к которому написан')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'
