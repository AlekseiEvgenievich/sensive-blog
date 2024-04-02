from django.contrib import admin
from blog.models import Post, Tag, Comment


admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Comment)


class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ["author", "likes", "tags"]
    list_display = ["title", "text", "published_at"]


class TagAdmin(admin.ModelAdmin):
    list_display = ["title"]


class CommentAdmin(admin.ModelAdmin):
     list_display = ('author', 'text', 'post', 'published_at') # Поля, которые будут отображаться в списке
     raw_id_fields = ('post',) 
