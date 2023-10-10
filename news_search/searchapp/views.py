from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.utils import timezone
from django.utils.timezone import make_aware
import requests
from .models import SearchQuery, SearchResult
from .forms import SignUpForm, SearchForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .utils import perform_search, check_recent_search, check_existing_query



def home(request):
    return render(request, 'searchapp/home.html')

@login_required
def search(request, query_id=None):
    """
    View for searching news articles based on a keyword or viewing saved search results.

    Parameters:
    - request: The HTTP request object.
    - query_id: (optional) The ID of a saved search query to view saved results.

    Returns:
    - If query_id is provided, it renders the saved search results associated with the query.
    - If a POST request is made with a valid search form, it performs a new search using an API,
      stores the results, and displays them.
    - If a GET request is made or if there are form validation errors, it displays the search form.

    Rate Limiting:
    - Prevents frequent searches for the same keyword within a set threshold (e.g., 15 minutes) to avoid excessive API requests.

    Refresh Logic:
    - If a search for an existing keyword is made after 15 minutes, it fetches new results using the API.
    - If the same keyword is searched within 15 minutes, it returns the existing results.

    """


    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query_text = form.cleaned_data['query'].lower()
            user = request.user

            # Check if the user has already searched for this query
            existing_query = SearchQuery.objects.filter(query=query_text, user=user).first()

            if existing_query:

                # Calculate the time elapsed since the last search
                time_elapsed = timezone.now() - existing_query.last_search_timestamp # type: ignore
                print(existing_query.last_search_timestamp, timezone.now)
                if time_elapsed >= timedelta(minutes=15):
                    print("sakhdgcnweirfhciufnchsejhcfnka")
                    # If it's been 15 minutes or more, perform a new search
                    # Perform the actual search using an API (code for this part is explained later)
                    search_results = perform_search(query_text, existing_query.last_search_timestamp)

                    # Clear the existing search results
                    SearchResult.objects.filter(query=existing_query).delete()

                    # Store the new search results in the database
                    for result in search_results:
                        search_result = SearchResult(
                            query=existing_query,
                            title=result['title'],
                            description=result['description'],
                            publishedAt=result['publishedAt'],
                            source_name=result['source']['name'],
                            source_category=result['source'].get('category', ''),
                            source_language=result['source'].get('language', ''),
                            source_url=result['url']
                        )
                        search_result.save()

                    # Update the last search timestamp for this query
                    existing_query.last_search_timestamp = datetime.now()
                    existing_query.save()

                    return render(request, 'searchapp/search.html', {'search_results': search_results, 'search_query': existing_query})
                else:
                    # If it's been less than 15 minutes, return the existing results
                    search_results = SearchResult.objects.filter(query=existing_query)
                    return render(request, 'searchapp/search.html', {'search_results': search_results, 'search_query': existing_query})
            else:
                # Perform the initial search
                search_results = perform_search(query_text, None)  # No last_timestamp for the initial search

                # Store the search query in the database
                search_query = SearchQuery(query=query_text, user=user)
                search_query.save()

                # Store the search results in the database
                for result in search_results:
                    search_result = SearchResult(
                        query=search_query,
                        title=result['title'],
                        description=result['description'],
                        publishedAt=result['publishedAt'],
                        source_name=result['source']['name'],
                        source_category=result['source'].get('category', ''),
                        source_language=result['source'].get('language', ''),
                        source_url=result['url']
                    )
                    search_result.save()

                # Update the last search timestamp for this query
                search_query.last_search_timestamp = datetime.now()
                search_query.save()

                return render(request, 'searchapp/search.html', {'search_results': search_results, 'search_query': search_query})
        
    
        elif query_id:
            # User wants to view a saved search result by query_id
            search_query = get_object_or_404(SearchQuery, pk=query_id, user=request.user)
            search_results = SearchResult.objects.filter(query=search_query)
            return render(request, 'searchapp/search.html', {'search_results': search_results, 'search_query': search_query})

        else:
            # todo: Handle form validation errors...
            pass
    else:
        form = SearchForm()
    return render(request, 'searchapp/search.html', {'form': form})
# @login_required(login_url='login')
# def search(request, query_id=None):
#     if request.method == 'POST':
#         form = SearchForm(request.POST)
#         if form.is_valid():
#             query_text = form.cleaned_data['query']
#             user = request.user

#             # Check if the user has made the same query within the last 15 minutes
#             recent_search = check_recent_search(query_text, user)

#             if not recent_search:
#                 # Perform the actual search using an API (code for this part is explained later)
#                 search_results = perform_search(query_text)

#                 # Store the search query in the database
#                 search_query = SearchQuery(query=query_text, user=user)
#                 search_query.save()

#                 # Store the search results in the database
#                 for result in search_results:
                    
#                     search_result = SearchResult(
#                         query=search_query,
#                         title=result['title'],
#                         description=result['description'],
#                         publishedAt=result['publishedAt'],
#                         source_name=result['source']['name'],
#                         source_category=result['source'].get('category', ''),
#                         source_language=result['source'].get('language', ''),
#                         source_url=result['url']
#                     )
#                     search_result.save()

#                     result['source_url'] = result['url']
#                     result['source_name'] = result['source']['name']

#                 return render(request, 'searchapp/search.html', {'search_results': search_results, 'search_query_id': query_id})
#             else:
#                 # Query the saved search results from the database
#                 search_results = SearchResult.objects.filter(query=recent_search)
#                 message = "You've made this query recently. Here are the results from your previous search:"
#                 return render(request, 'searchapp/search.html', {'search_results': search_results, 'message': message})
    
#     return render(request, 'searchapp/search.html', {'form': form})
   
               
@login_required
def search_history(request):
    """
    View for displaying the search history of a user, including saved search queries and results.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - Renders a page displaying the search history, including saved search queries and results.
    - Allows users to click on saved queries to view their results.
    """

    user = request.user
    search_queries = SearchQuery.objects.filter(user=user).order_by('-last_search_timestamp')
    return render(request, 'searchapp/search_history.html', {'search_queries': search_queries})


@login_required # type: ignore
def search_refresh(request):
    """
    View for refreshing (fetching the latest) search results for a specific keyword.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - If a POST request is made, it retrieves the keyword from the form, performs a new search using an API,
      and updates the search results in the database.
    - Redirects the user back to the search results page to display the refreshed results.

    Authentication:
    - Requires user authentication.

    Rate Limiting:
    - Inherits the rate limiting logic from the main search view to prevent frequent searches for the same keyword
      within a set threshold (e.g., 15 minutes).
    """

    if request.method == 'POST':
        query_text = request.POST.get('query')
        user = request.user

        # Check if the user has already searched for this query
        existing_query = SearchQuery.objects.filter(query=query_text, user=user).first()

        if existing_query:
            # Calculate the time elapsed since the last search
            time_elapsed = datetime.now() - existing_query.last_search_timestamp

            if time_elapsed.total_seconds() >= 900:  # 15 minutes = 900 seconds
                # If it's been 15 minutes or more, perform a new search
                # Perform the actual search using an API (code for this part is explained later)
                search_results = perform_search(query_text, existing_query.last_search_timestamp)

                # Clear the existing search results
                SearchResult.objects.filter(query=existing_query).delete()

                # Store the new search results in the database
                for result in search_results:
                    search_result = SearchResult(
                        query=existing_query,
                        title=result['title'],
                        description=result['description'],
                        source_name=result['source_name'],
                        source_url=result['source_url'],
                        published_at=result['published_at']
                    )
                    search_result.save()

                # Update the last search timestamp for this query
                existing_query.last_search_timestamp = datetime.now()
                existing_query.save()
        else:
            # Perform the actual search using an API
            search_results = perform_search(query_text)
        # todo: store the search results
        # pass it to template along with a success message
        return redirect('search')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST) 
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('search')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                # Redirect to a specific page after successful login (e.g., the search page)
                return redirect('search')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')

    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
