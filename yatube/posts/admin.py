from django.contrib import admin

from core.admin import BaseAdmin
from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    search_fields = ("title",)
    empty_value_display = "-пусто-"


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'post')
    search_fields = ('post',)
    list_filter = ('pub_date',)
    list_editable = ('text',)


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    list_display = (
        'pk',
        'author',
        'user',
    )
    search_fields = ('author',)
    list_filter = ('author',)
