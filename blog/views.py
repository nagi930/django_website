from django.shortcuts import render
from .models import Post, Category, Tag
from django.views.generic import ListView, DetailView

class PostList(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['post_without_category'] = Post.objects.filter(category=None).count()

        return context

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['post_without_category'] = Post.objects.filter(category=None).count()

        return context

class PostListByTag(ListView):
    def get_queryset(self):
        tag_slug = self.kwargs['slug']
        tag = Tag.objects.get(slug=tag_slug)

        return tag.post_set.order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['post_without_category'] = Post.objects.filter(category=None).count()
        tag_slug = self.kwargs['slug']
        context['tag'] = Tag.objects.get(slug=tag_slug)

        return context

class PostListByCategory(PostList):

    def get_queryset(self):
        slug = self.kwargs['slug']

        if slug == '_none':
            category = None
        else:
            category = Category.objects.get(slug=slug)

        return Post.objects.filter(category=category).order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(type(self),self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['post_without_category'] = Post.objects.filter(category=None).count()

        slug = self.kwargs['slug']
        if slug == '_none':
            category = '미분류'
        else:
            category = Category.objects.get(slug=slug)
            context['category'] = category


        context['title'] = 'Blog - {}'.format(category)

        return context

# def post_detail(request, pk):
#     blog_post = Post.objects.get(pk=pk)
#
#     return render(
#         request,
#         'blog/post_detail.html',
#         {
#             'blog_post' : blog_post
#         }
#     )

# def index(request):
#     posts = Post.objects.all()
#     return render(
#         request,
#         'blog/index.html',
#         {
#             'posts':posts,
#         }
#     )
