from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.menu_page, name='menu'),
    path('menu/', views.menu_page, name='menu_page'),
    path('admin-panel/', views.admin_page, name='admin_page'),

    # APIs
    path('api/decode/', views.decode_token_api, name='decode_token'),
    path('api/generate-qr/', views.generate_qr, name='generate_qr'),
    path('api/menu/', views.menu_api, name='menu_api'),
    path('api/menu/<int:item_id>/', views.menu_item_api, name='menu_item_api'),
    path('api/order/', views.create_order, name='create_order'),
    path('api/orders/', views.get_orders, name='get_orders'),
    path('api/orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('dashboard/', views.analytics_page),
    path('analytics', views.get_analytics),
    path('ai-suggestions', views.ai_suggestions),
]
