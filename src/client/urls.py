from django.urls import path
from . import views
from .views import reservation_form
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.client_dashboard, name='client_dashboard'),
    path(
        "reservation/<slug:slug>/",
        reservation_form,
        name="reservation_form"
    ),
    path(
    "logout/",
    LogoutView.as_view(next_page="vehicle_list"),
    name="logout",
    ),
    path(
    "delete-account/",
    views.delete_account,
    name="delete_account"
    ),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
]

