from django.urls import path
from courses import views

urlpatterns = [
    # Gestion des forfaits
    path('packages/', views.package_list, name='package_list'),
    path('packages/<int:pk>/', views.package_detail, name='package_detail'),
    path('packages/create/', views.package_create, name='package_create'),
    path('packages/<int:pk>/edit/', views.package_edit, name='package_edit'),
    path('packages/<int:pk>/delete/', views.package_delete, name='package_delete'),
    
    # Gestion des achats
    path('purchase/<int:package_id>/', views.purchase_package, name='purchase_package'),
    path('purchases/', views.purchase_history, name='purchase_history'),
    
    # Espace comptabilité
    path('accounting/', views.accounting_dashboard, name='accounting_dashboard'),
]