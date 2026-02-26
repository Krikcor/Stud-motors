from django.urls import path
from . import views

urlpatterns = [
    path("", views.vehicle_list, name="vehicle_list"),
    path("<slug:slug>/", views.vehicle_detail, name="vehicle_detail"),
]