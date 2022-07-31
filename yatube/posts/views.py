from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow

NUMBER_OF_POSTS: int = 10



def paginator_group(request, post_list):
    paginator = Paginator(post_list, NUMBER_OF_POSTS)
    page_number = request.GET.get('page_obj')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.select_related('author', 'group').all()
    page_obj = paginator_group(request, post_list)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.select_related('author').all()
    page_obj = paginator_group(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username): # проверить этот вариант
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group').all()
    page_obj = paginator_group(request, post_list)
    following = (request.user.is_authenticated
                and Follow.objects.filter(
                user=request.user,
                author=author).exists())
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following}
    return render(request, template, context)
# def profile(request, username):
#     author = get_object_or_404(User, username=username)
#     post_list = Post.objects.filter(author=author)
#     page_obj = paginator_group(request, post_list)
#     following = (request.user.is_authenticated
#                 and Follow.objects.filter(
#                     user=request.user,
#                     author=author).exists())
#     context = {
#         'author': author,
#         'page_obj': page_obj,
#         'following': following
#     }
#     return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments}
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)
    if request.method == 'POST':
        form = PostForm(request.POST or None,
                        files=request.FILES or None,
                        instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


# def page_not_found(request):
#     # Переменная exception содержит отладочную информацию,
#     # выводить её в шаблон пользователской страницы 404 мы не станем
#     return render(
#         request,
#         "misc/404.html",
#         {"path": request.path},
#         status=404
#     )


# def server_error(request):
#     return render(request, "misc/500.html", status=500)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_group(request, posts_list)
    context = {'page_obj': page_obj}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    Follow.objects.filter(user=user, author__username=username).delete()
    return redirect("posts:profile", username=username)
