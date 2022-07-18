
from re import template
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import PostForm
from .models import Group, Post, User


POST_COUNT = 10
OUTPUT_OF_POSTS = 30
NUMBER_OF_POSTS: int = 10

def paginator_group(request, post_list):
    paginator = Paginator(post_list, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page

def index(request):
    post_list = Post.objects.select_related('author', 'group').all()
    # paginator = Paginator(post_list, POST_COUNT)
    # page_number = request.GET.get('page')
    page = paginator_group(request, post_list)
    context = {
        'page': page,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.select_related('author').all()
    page = paginator_group(request, post_list)
    #posts = group.posts.all()
    #paginator = Paginator(posts, POST_COUNT)
    #page_number = request.GET.get('page')
    #page = paginator.get_page(page_number)
    context = {
        'group': group,
        'page': page,
    }
    return render(request, 'posts/group_list.html', context)

def profile(request, username):
    author = get_object_or_404(User, username=username) 
    post_list = author.posts.select_related('group').all()
    page = paginator_group(request, post_list)
    # paginator = Paginator(author.posts.all(), POST_COUNT)
    # page_number = request.GET.get('page')
    # page = paginator.get_page(page_number)
    context = {
        'author': author, 
        'page': page
}
    return render(request, 'posts/profile.html',context)

def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    # pub_date = post.pub_date
    # post_title = post.text[:OUTPUT_OF_POSTS]
    # author = post.author
    # author_posts = author.posts.all().count()
    # context = {
    #     'post': post},
        # 'post_title': post_title,
        # 'author': post.author,
        # 'author_posts': author_posts,
        # 'pub_date': pub_date
    
    return render(request, template, {'post': post})


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
    # if request.method == 'POST':
    #     form = PostForm(request.POST or None,
    #                 files=request.FILES or None)
    #     #form = PostForm(request.POST)
    #     if form.is_valid():
    #         post = form.save(commit=False)
    #         post.author = request.user
    #         post.save()
    #         return redirect(f'/profile/{post.author}/', {'form': form})
    # form = PostForm()
    # groups = Group.objects.all()
    # context = {'form': form, 'groups': groups}
    # return render(request, 'posts/create_post.html', context)


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
        'is_edit': True
    }
    return render(request, template, context)
    # post = get_object_or_404(Post, id=post_id)
    # groups = Group.objects.all()
    # if request.user != post.author:
    #     return redirect("posts:post_detail", post_id)
    # form = PostForm(request.POST or None, instance=post)
    # template = "posts/create_post.html"
    # if form.is_valid():
    #     form.save()
    #     return redirect("posts:post_detail",
    #     post_id=post_id)
    # context = {
    #     "form": form,
    #     "is_edit": True,
    #     "post": post
    # }
    # return render(request, template, context)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)