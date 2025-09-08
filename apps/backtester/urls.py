from django.urls import path
from . import views

urlpatterns = [
    path('', views.BacktestListView.as_view(), name='backtest_list'),
    path('new/', views.BacktestCreateView.as_view(), name='backtest_create'),
    path('<int:backtest_id>/', views.BacktestDetailView.as_view(), name='backtest_detail'),
    path('<int:backtest_id>/delete/', views.BacktestDeleteView.as_view(), name='backtest_delete'),
]