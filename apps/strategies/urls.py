from django.urls import path
from . import views

urlpatterns = [
    path("get-strategy-schema/<int:strategy_id>/", views.get_strategy_schema, name="get_strategy_schema"),
]
