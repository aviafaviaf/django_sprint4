from typing import Any
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from .models import Post, Category, Comment
from django.db.models import Count
from django.utils.timezone import localdate
from django.http import HttpResponseNotFound
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from .forms import CommentForm, UserEditForm

User = get_user_model()

class HomePage(TemplateView):
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        post_list = Post.objects.filter(
            pub_date__lte=localdate(),
            is_published=True,
            category__is_published=True)\
            .annotate(comment_count=Count("comments"))\
            .order_by('pub_date').reverse()

        paginator = Paginator(post_list, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(Category, slug=category_slug)
    post_list = Post.objects.filter(
        pub_date__lte=localdate(),
        is_published=True,
        category__slug=category_slug)\
        .annotate(comment_count=Count("comments"))\
        .order_by('pub_date').reverse()

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj
    }
    if category.is_published:
        return render(request, template_name, context)
    return HttpResponseNotFound()


def post_detail(request, id):
    template_name = 'blog/detail.html'
    post = get_object_or_404(Post, id=id)
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': Comment.objects.filter(post__id=id)
    }
    if post.is_published and post.category.is_published\
            and post.pub_date.date() <= localdate()\
            or post.author == request.user:
        return render(request, template_name, context)
    return HttpResponseNotFound()


class PostCreate(CreateView):
    model = Post
    fields = ('title', 'text', 'location', 'category', 'is_published',
              'pub_date', 'image')
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            args=[self.request.user.username])

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class DeletePost(DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(
            Post,
            pk=kwargs['pk'],
        )
        if post.author != request.user:
            return redirect('blog:post_detail', id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class UpdatePost(UpdateView):
    model = Post
    fields = '__all__'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(
            Post,
            pk=kwargs['pk'],
        )
        if post.author != request.user:
            return redirect('blog:post_detail', id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class UpdateComment(UpdateView):
    model = Comment
    field = ('text',)
    form_class = CommentForm
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comment,
            pk=kwargs['pk'],
        )
        if comment.author != request.user:
            return redirect('blog:post_detail', id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class DeleteComment(DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comment,
            pk=kwargs['pk'],
        )
        if comment.author != request.user:
            return redirect('blog:post_detail', id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', id=post.pk)


def user_profile(request, username):
    template_name = 'blog/profile.html'
    user = get_object_or_404(User, username=username)

    if request.user.username != user.username:
        post_list = post_list = Post.objects.filter(
            pub_date__lte=localdate(),
            is_published=True,
            author__username=user.username)\
            .annotate(comment_count=Count("comments"))\
            .order_by('pub_date').reverse()
    else:
        post_list = Post.objects.filter(
            author__username=user.username).order_by('pub_date').reverse()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


class EditProfile(UpdateView):
    form_class = UserEditForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user
