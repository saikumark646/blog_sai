from django.contrib.sitemaps import Sitemap

from .models import Post


class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9
# The changefreq and priority attributes indicate the change frequency of your post pages and their relevance in your website (the maximum value is 1).

    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.updated
    # The lastmod method receives each object returned by items() and returns the lasttime the object was modified.
