from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "currency", "created_at")
    list_filter = ("category", "currency")
    search_fields = ("name", "category", "description")
