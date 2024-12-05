from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.portfolio, name='portfolio'),
    path('fetch-news/', views.fetch_portfolio_news, name='fetch_portfolio_news'),
    path('trading-log/', views.trading_log_view, name='trading_log'),
]
