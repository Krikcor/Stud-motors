from django.urls import path
from . import views
from .views import reservation_form

urlpatterns = [
    path('', views.client_dashboard, name='client_dashboard'),
    path(
        "reservation/<slug:slug>/",
        reservation_form,
        name="reservation_form"
    ),
]