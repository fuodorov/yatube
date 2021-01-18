from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from posts.constants import POSTS_PER_PAGE

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.select_related("group")
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
         request,
         "index.html",
         {"page": page, "paginator": paginator}
     )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "posts/group.html",
        {"page": page, "paginator": paginator, "group": group}
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("index")
    return render(request, "posts/new_post.html", {"form": form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    try:
        following = Follow.objects.filter(
            user__username=request.user,
            author__username=author
        ).exists()
    except TypeError:
        following = True
    return render(
        request,
        "posts/profile.html",
        {"page": page,
         "paginator": paginator,
         "author": author,
         "following": following}
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    items = post.comments.all()
    return render(
        request,
        "posts/post.html",
        {
            "author": post.author,
            "post": post,
            "items": items,
            "form": CommentForm()
            }
    )


@login_required
def post_edit(request, username, post_id):
    current_user = request.user
    post = get_object_or_404(
        Post,
        author=request.user,
        author__username=username,
        pk=post_id
    )
    author_user = post.author
    if current_user != author_user:
        return redirect("index")
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(
            "post",
            username=username,
            post_id=post_id
        )
    return render(
        request,
        "posts/new_post.html",
        {"form": form, "post": post}
    )


def page_404(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def page_500(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        form.save()
        return redirect("post", username=username, post_id=post_id)
    return render(
        request,
        "posts/include/comment.html",
        {"form": form, "comments": comments}
    )


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "posts/follow.html",
        {"page": page, "paginator": paginator}
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    unfollow = Follow.objects.get(
        user=request.user,
        author=author
    )
    unfollow.delete()
    return redirect("profile", username=username)
