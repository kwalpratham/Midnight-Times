from django.db import models
from django.contrib.auth.models import User

class SearchQuery(models.Model):
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    # last_search_timestamp = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.query

class SearchResult(models.Model):
    query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    publishedAt = models.DateTimeField()
    source_name = models.CharField(max_length=255)
    source_category = models.CharField(max_length=255)
    source_language = models.CharField(max_length=10)
    source_url = models.URLField()

    def __str__(self):
        return self.title
