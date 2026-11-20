from django.urls import path

from . import views


urlpatterns = [
    path("", views.product_create, name="product_create"),
    path("products/", views.product_list, name="product_list"),
]
