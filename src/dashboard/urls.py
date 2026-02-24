from django.urls import path
from . import views

urlpatterns = [
    path('', views.pro_dashboard, name='pro_dashboard'),
    path("vehicles/create/", views.create_vehicle, name="create_vehicle"),
    path("vehicle/delete/", views.delete_vehicle, name="delete_vehicle"),
    path("vehicle/modify/", views.modify_vehicle, name="modify_vehicle"),
]
