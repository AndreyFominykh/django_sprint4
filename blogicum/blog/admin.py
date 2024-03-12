from django.contrib import admin

from .models import Category, Location, Post, Comment


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'is_published', 'slug',
                    'created_at')
    list_filter = ('title', 'is_published')


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'is_published')


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'pub_date', 'category', 'is_published',
                    'location', 'created_at')
    list_filter = ('author', 'is_published', 'location', 'category')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
