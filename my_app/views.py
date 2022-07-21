from my_app.forms import SearchForm
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Count
from taggit.models import Tag
from django.core.mail import send_mail
from .forms import EmailPostForm, CommentForm
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.


def post_list(request, tag_slug=None):
    qs = Post.published.all()                        # with custom model manager
    tag = None
    # qs = Post.objects.filter(status='published')    #if without custom model manager
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        qs = qs.filter(tags__in=[tag])
    paginator = Paginator(qs, 2)        # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'my_app/post/list.html',
                  {'page': page,
                   'posts': posts,
                   'tag': tag})


def post_detail(request, year, post, month, day):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,
                             )
    # considering only active comments
    comments = post.comments.filter(active=True)
    # initialize the new_comment variable by setting it to None.
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            # we are assingned that comment form to new_comment and not saving in the data base
            new_comment = comment_form.save(commit=False)
            new_comment.post = post  # assigning the post to the perticular comment
            new_comment.save()
    else:
        # if form not subbmitted, it will return empty form.
        comment_form = CommentForm()

    post_tags_ids = Post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count(
        'tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'my_app/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'comment_form': comment_form,
                   'new_comment': new_comment,
                   'similar_posts': similar_posts
                   })


# class PostListView(ListView):  # class based list view
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'my_app/post/list.html'


def post_share(request, post_id):
    # You use the get_object_or_404() shortcut to retrieve the post by ID and make sure that the retrieved post has a published status.
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':        # if form is submitted
        # we will take take the submitted form
        form = EmailPostForm(request.POST)
        if form.is_valid():                 # check form is valid or not
            cd = form.cleaned_data         # if valid send mail
            post_url = request.build_absolute_uri(
                post.get_absolute_url())          # we are building a post url by taking get_absolute_url as input, (we are sharing a post by urlso we need to create a url)
            subject = f"{cd['name']} recommends you read " \
                f"{post.title}"                                   # data tobe print at terminal
            message = f"Read {post.title} at {post_url}\n\n" \
                f"{cd['name']}\'s comments: {cd['comments']}"    # data tobe print at terminal
            # data tobe print at terminal
            send_mail(subject, message, [cd['email']], [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'my_app/post/share.html',
                  {'form': form,
                   'post': post,
                   'sent': sent})

# What is annotate and aggregate in Django?
# Aggregate calculates values for the entire queryset. Annotate calculates summary values for each item in the queryset.


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_query = SearchQuery(query)
            search_vector = SearchVector('title', 'body')
            results = Post.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)).filter(search=search_query).order_by('-rank')

    return render(request, 'my_app/post/search.html',
                  {
                      'form': form,
                      'query': query,
                      'results': results
                  })
# This proj done upto Stemming and ranking results chapter 3,
