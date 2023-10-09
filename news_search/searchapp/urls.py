from django.urls import path
from searchapp import views


# app urls
urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search, name='search'),
    path('search/<int:query_id>/', views.search, name='search_results'),
    path('search_history/', views.search_history, name='search_history'),
    path('search_refresh/', views.search_refresh, name='search_refresh')
    
]
