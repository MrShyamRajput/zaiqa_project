from django.contrib import admin
from .models import MenuItem, Order

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'stock', 'available']
    list_filter = ['category', 'available']
    search_fields = ['name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'table_number', 'total', 'status', 'created_at']
    list_filter = ['status']
