from django.urls import path
from . import views

urlpatterns = [
    path("", views.BacktestListView.as_view(), name="backtest_list"),
    path("new/", views.BacktestCreateView.as_view(), name="backtest_create"),
    path(
        "<int:backtest_id>/", views.BacktestDetailView.as_view(), name="backtest_detail"
    ),
    path(
        "<int:backtest_id>/delete/",
        views.BacktestDeleteView.as_view(),
        name="backtest_delete",
    ),
    path("get-property-schema/<str:backtest_type>/<int:strategy_id>/", views.get_property_schema_view, name="get_property_schema"),
]
