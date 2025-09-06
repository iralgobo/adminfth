from django.urls import path
from . import views

urlpatterns = [
    path(
        "configurations/",
        views.tracking_configuration_list,
        name="tracking_configuration_list",
    ),
    path(
        "configurations/view/<int:pk>/",
        views.tracking_configuration_detail,
        name="tracking_configuration_detail",
    ),
    path(
        "configurations/create/",
        views.tracking_configuration_create,
        name="tracking_configuration_create",
    ),
    path(
        "configurations/update/<int:pk>/",
        views.tracking_configuration_update,
        name="tracking_configuration_update",
    ),
    path(
        "configurations/delete/",
        views.tracking_configuration_delete,
        name="tracking_configuration_delete",
    ),
    path(
        "configurations/ajax/",
        views.tracking_configuration_list_ajax,
        name="tracking_configuration_list_ajax",
    ),
    path(
        "candles/<int:tracking_configuration_id>/",
        views.candle_list_view,
        name="candle_list",
    ),
    path(
        "candles/ajax/<int:tracking_configuration_id>/",
        views.candle_list_ajax,
        name="candle_list_ajax",
    ),
]
