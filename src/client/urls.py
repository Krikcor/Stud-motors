from django.urls import path
from . import views

urlpatterns = [
    path('', views.client_dashboard, name='client_dashboard'),
    path('reservation/<slug:slug>/', views.reservation_form, name='reservation_form'),
]