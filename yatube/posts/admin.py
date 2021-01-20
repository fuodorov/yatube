from django.contrib import admin

from .models import Comment, Group, Post, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "text",
        "pub_date",
        "author",
        "group",
        "image",
    )
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "title",
        "slug",
        "description",
    )
    search_fields = ("title",)
    empty_value_display = "-пусто-"


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "post",
        "text",
        "author",
        "created",
    )
    search_fields = ("text",)
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "author",
        "user"
    )
    list_filter = ("author", "user")


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
