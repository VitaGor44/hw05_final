from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from http import HTTPStatus
from django.shortcuts import render, get_object_or_404, redirect, reverse

from django.core.paginator import Paginator
from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow


POST_PAGES = 10


def get_page_context(request, queryset):
    paginator = Paginator(request, POST_PAGES)
    page_number = queryset.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }


def index(request):
    context = get_page_context(Post.objects.all(), request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:POST_PAGES]
    context = {
        'group': group,
        'posts': posts,
    }
    context.update(get_page_context(group.posts.all(), request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = (
        request.user.is_authenticated and Follow.objects.filter(
            user=request.user, author=author,
        ).exists()
    )
    context = {
        'author': author,
        'following': following,
    }
    context.update(get_page_context(author.posts.all(), request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    count = post.author.posts.count()
    context = {
        'post': get_object_or_404(Post, pk=post_id),
        'count': count,
        'is_edit': post.author == request.user,
        'comment_form': CommentForm(),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail',
                        post_id=post_id
                        )
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': True, 'post_id': post_id}
                  )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comment_list = post.comments.all()
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(
        request, 'posts/include/comments.html', {
            'form': form, "comments": comment_list}
    )


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(
        author__following__user=request.user.id
    ).select_related('author', 'group')
    page_obj = Paginator(posts_list, POST_PAGES)
    page_number = request.GET.get('page')
    page = page_obj.get_page(page_number)
    context = {'page_obj': page}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """
    Подписка на автора
    """
    user = request.user
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=user, author=author)
    if user != author and not is_follower.exists():
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect(reverse('posts:profile', args=[username]))


@login_required
def profile_unfollow(request, username):
    """
    Дизлайк, отписка
    """
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    is_follower.delete()
    return redirect('posts:profile', username=author)


@login_required
def post_delete(request, username, post_id):
    if request.user.username != username:
        return redirect('posts:post', username, post_id)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    post.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def page_not_found(request, exception):
    return render(
        request, "core/404.html", {
            "path": request.path
        }, status=HTTPStatus.NOT_FOUND
    )


def server_error(request):
    return render(request, "core/500.html", status=500)


def permission_denied(request, exception):
    return render(request, 'core/403.html', status=403)
