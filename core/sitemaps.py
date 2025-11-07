# core/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "weekly"

    def items(self):
        return ["home", "compare-prices", "login-page", "signup-page"]

    def location(self, item):
        return reverse(item)
