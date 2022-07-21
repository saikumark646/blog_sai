from django.urls import path
from . import views
from .feeds import latestPostsFeed
app_name = "my_app"
urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('<int:year>/<slug:post>/<int:month>/<int:day>/',
         views.post_detail, name='post_detail'),

    path('<int:post_id>/share', views.post_share, name='post_share'),

    #path('', views.PostListView.as_view(), name='post_list'),

    path('tag/<slug:tag_slug>', views.post_list, name='post_list_by_tag'),

    path('feed/', latestPostsFeed(), name='post_feed'),
    path('search', views.post_search, name='post_search')
]
