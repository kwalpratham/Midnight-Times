from datetime import datetime
import os
from .models import SearchQuery
from django.utils import timezone
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
BASE_URL = os.getenv('BASE_URL')
pagesize = os.getenv('pagesize')


def perform_search(query_text, from_timestamp = None):
    """
    Perform a search for news articles based on a keyword and retrieve the results from an external API.

    Parameters:
    - query: The keyword or phrase to search for.
    - from_timestamp: (optional) The timestamp indicating the date and time of the last search.
      If provided, fetch only news articles published after this timestamp.

    Returns:
    - A list of dictionaries, where each dictionary represents a news article with the following keys:
      - 'title': The title of the article.
      - 'description': The description or summary of the article.
      - 'source_name': The name of the news source.
      - 'source_url': The URL of the news source.
      - 'published_at': The date and time when the article was published.

    API Integration:
    - This function integrates with an external news API to fetch news articles based on the provided query.
    - It includes support for filtering articles based on the provided 'from_timestamp' to retrieve only new articles.

    Error Handling:
    - Handles API request errors and returns an empty list in case of errors.

    Usage Example:
    - Example usage within the Django application's views to fetch search results for a keyword.

    """
    
    params = {
        'q': query_text,
        'apiKey': NEWS_API_KEY,
        'pageSize': pagesize,
        'language': 'en',
        'sortBy': 'publishedAt',
        'from': from_timestamp
    }

    url = BASE_URL + '/everything'

    response = requests.get(url, params=params)
    print("hello i should get printed")
    if response.status_code == 200:
        data = response.json()
        return data.get('articles', [])
    else:
        # Error Logger
        print(f"Api response error: {response.status_code}")
        return []


def check_existing_query(query_text, user):
    existing_query = SearchQuery.objects.filter(query=query_text, user=user).first()
    # time_elapsed = datetime.now() - existing_query.last_search_timestamp
    return existing_query


def check_recent_search(query_text, user):
    threshold_minutes = 15
    recent_search = SearchQuery.objects.filter(
        query=query_text,
        user=user,
        created_at__gte=timezone.now() - timezone.timedelta(minutes=threshold_minutes)
    ).first()
    return recent_search