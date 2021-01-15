from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from posts import constants

from .models import Post, Group
from .forms import PostForm


def index(request):
    post_list = Post.objects.select_related('group').order_by('-pub_date')
    paginator = Paginator(post_list, constants.posts_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
         request,
         'index.html',
         {'page': page, }
     )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, constants.posts_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "posts/group.html",
        {'page': page, 'paginator': paginator, 'group': group}
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("index")
    return render(request, "posts/new_post.html", {"form": form})
