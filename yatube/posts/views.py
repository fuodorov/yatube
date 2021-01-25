from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User
from posts.settings import POSTS_PER_PAGE


def is_user_subscribed(user, author):
    return (user != author and
            user.is_authenticated and
            Follow.objects.filter(user=user, author=author).exists())


def is_authenticated_user_subscribed(user, author):
    return (user != author and
            Follow.objects.filter(user=user, author=author).exists())


def index(request):
    post_list = Post.objects.select_related("group")
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {
        "page": page,
        "paginator": paginator
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "posts/group.html", {
        "page": page,
        "paginator": paginator,
        "group": group
    })


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, "posts/new_post.html", {"form": form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("index")


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    following = is_user_subscribed(request.user, author)
    return render(request, "posts/profile.html", {
        "page": page,
        "paginator": paginator,
        "author": author,
        "following": following
    })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    comments = post.comments.all()
    following = is_user_subscribed(request.user, post.author)
    return render(request, "posts/post.html", {
        "author": post.author,
        "post": post,
        "comments": comments,
        "form": CommentForm(),
        "following": following
    })


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    if request.user != post.author:
        return redirect("post", username=username, post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if not form.is_valid():
        return render(request, "posts/new_post.html", {
            "form": form,
            "post": post
        })
    form.save()
    return redirect("post", username=username, post_id=post_id)


def page_404(request, exception):
    return render(request, "misc/404.html", {"path": request.path},
                  status=404)


def page_500(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, "posts/include/comment.html", {
            "form": form,
            "comments": post.comments.all()
        })
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect("post", username=username, post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "posts/follow.html", {
        "page": page,
        "paginator": paginator
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if not is_authenticated_user_subscribed(request.user, author):
        Follow.objects.create(user=request.user, author=author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    follow = get_object_or_404(Follow, user=request.user,
                               author__username=username)
    follow.delete()
    return redirect("profile", username=username)
