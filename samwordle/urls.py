from django.urls import path

from . import views

urlpatterns = [
    path("", views.request_wordle, name="request_wordle"),
]
