from django.contrib import admin
from .models import Post, Comment
# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish', 'updated', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body', 'author')
    # to consider title as slug automatically
    prepopulated_fields = {'slug': ('title',)}
    # raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'name', 'email', 'created', 'active')
    list_filter = ('active', 'created')
    search_fields = ('name', 'email')
